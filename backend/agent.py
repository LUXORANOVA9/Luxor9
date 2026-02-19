import json
import os
import asyncio
from typing import List, Dict, Optional, Callable
from datetime import datetime
from collections import defaultdict
import re

from llm_router import FreeLLMRouter, LLMResponse
from tools.base import get_all_tools, BaseTool, ToolResult
from config import settings

class Agent:
    """
    Autonomous agent — reasons and acts using tools.

    Loop: Think → Act → Observe → Repeat
    Providers: Groq → Gemini → Cloudflare → Ollama (all free)
    Database: Neon PostgreSQL (async)
    """

    def __init__(
        self,
        name: str,
        role: str,
        llm_router: FreeLLMRouter,
        workspace_path: str,
        event_callback: Callable,
        database=None,
        system_prompt_extra: str = "",
    ):
        self.name = name
        self.role = role
        self.llm = llm_router
        self.workspace = workspace_path
        self.emit = event_callback
        self.db = database
        self.extra_prompt = system_prompt_extra

        self.tools = get_all_tools()
        self.tool_map = {t.name: t for t in self.tools}

        self.messages: List[Dict] = []
        self.turn_count = 0
        self.total_tokens = 0
        self.is_cancelled = False
        self.injected_messages: List[str] = []
        self.provider_stats: Dict[str, int] = defaultdict(int)

        os.makedirs(workspace_path, exist_ok=True)

    def _system_prompt(self) -> str:
        return f"""You are Luxor9, an AI agent that autonomously completes tasks using tools.

## Rules
1. Execute ONE tool per response.
2. ALWAYS start by creating todo.md with your plan.
3. Update todo.md after completing each step (mark [x]).
4. Verify your work before finishing.
5. When fully done, respond with a summary and NO tool call.

## Workspace
All files: {self.workspace}
Use relative paths.

## Available Tools
Use the <tool_call> format to call tools.

{self.extra_prompt}

IMPORTANT: When task is complete, write your final summary as plain text WITHOUT any <tool_call> tags."""

    async def run(self, task: str) -> str:
        self.messages.append({
            "role": "user",
            "content": f"Task: {task}\n\nStart by creating todo.md with your plan."
        })

        tool_schemas = [t.to_schema() for t in self.tools]
        system = self._system_prompt()

        while self.turn_count < settings.MAX_AGENT_TURNS and not self.is_cancelled:
            self.turn_count += 1

            # Check for injected human messages
            if self.injected_messages:
                msg = self.injected_messages.pop(0)
                self.messages.append({"role": "user", "content": f"[Human message]: {msg}"})

            # === THINK ===
            try:
                response = await self.llm.generate(
                    messages=self.messages,
                    tools=tool_schemas,
                    system=system,
                    temperature=0.0,
                    max_tokens=4096,
                )
            except Exception as e:
                await self.emit({
                    "type": "error",
                    "agent_name": self.name,
                    "content": {"error": f"LLM error: {e}"}
                })
                await asyncio.sleep(3)
                continue

            self.total_tokens += response.input_tokens + response.output_tokens
            self.provider_stats[response.provider] += 1

            if response.tool_calls:
                tc = response.tool_calls[0]

                # Emit thought (cleaned of tool_call tags)
                if response.content.strip():
                    cleaned = self._strip_tool_calls(response.content)
                    if cleaned.strip():
                        await self.emit({
                            "type": "thought",
                            "agent_name": self.name,
                            "content": {
                                "text": cleaned,
                                "provider": response.provider,
                                "model": response.model,
                            }
                        })

                # Emit tool call
                await self.emit({
                    "type": "tool_call",
                    "agent_name": self.name,
                    "content": {
                        "tool": tc["name"],
                        "arguments": tc["arguments"],
                        "turn": self.turn_count,
                        "provider": response.provider,
                    }
                })

                # === ACT ===
                result = await self._exec_tool(tc["name"], tc["arguments"])

                # Log to Neon DB (async)
                if self.db:
                    try:
                        await self.db.log_turn(
                            task_id=self.name,
                            agent_name=self.name,
                            turn_number=self.turn_count,
                            tool_name=tc["name"],
                            tool_input=tc["arguments"],
                            tool_output=result.output[:5000],
                            reasoning=response.content[:2000],
                            model_used=response.model,
                            provider=response.provider,
                            input_tokens=response.input_tokens,
                            output_tokens=response.output_tokens,
                            latency_ms=response.latency_ms,
                        )
                    except Exception:
                        pass  # Don't crash agent on DB error

                # Emit result
                event_content = {
                    "tool": tc["name"],
                    "success": result.success,
                    "output": result.output[:3000],
                }

                # Screenshot handling
                if result.artifacts.get("screenshot"):
                    await self.emit({
                        "type": "screenshot",
                        "agent_name": self.name,
                        "content": {"image": result.artifacts["screenshot"]}
                    })

                await self.emit({
                    "type": "tool_result",
                    "agent_name": self.name,
                    "content": event_content,
                })

                # Plan update detection
                if tc["name"] == "file_write" and "todo.md" in tc["arguments"].get("path", ""):
                    await self.emit({
                        "type": "plan_update",
                        "agent_name": self.name,
                        "content": {"plan": tc["arguments"].get("content", "")}
                    })

                # === OBSERVE ===
                self.messages.append({
                    "role": "assistant",
                    "content": response.content,
                })
                self.messages.append({
                    "role": "user",
                    "content": f"Tool [{tc['name']}] result:\n{result.output[:8000]}"
                    + (f"\nError: {result.error}" if result.error else "")
                })

                # Context window management
                if len(self.messages) > 30:
                    self._compress()

            else:
                # === DONE ===
                summary = response.content

                await self.emit({
                    "type": "thought",
                    "agent_name": self.name,
                    "content": {"text": summary}
                })

                return summary

        return f"Stopped after {self.turn_count} turns."

    async def _exec_tool(self, name: str, args: dict) -> ToolResult:
        tool = self.tool_map.get(name)
        if not tool:
            return ToolResult(False, "", f"Unknown tool: {name}. Available: {list(self.tool_map.keys())}")

        ctx = {"workspace_path": self.workspace, "task_id": self.name}

        try:
            return await asyncio.wait_for(tool.execute(args, ctx), timeout=120)
        except asyncio.TimeoutError:
            return ToolResult(False, "", f"Tool {name} timed out")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def _compress(self):
        """Compress old conversation to stay in context window."""
        if len(self.messages) <= 15:
            return
        old = self.messages[1:-12]
        summary = "Previous steps summary:\n"
        for m in old[-8:]:
            summary += f"- {str(m.get('content', ''))[:150]}\n"
        self.messages = [self.messages[0], {"role": "user", "content": summary}] + self.messages[-12:]

    def _strip_tool_calls(self, text: str) -> str:
        return re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL).strip()

    def inject_message(self, msg: str):
        """Human-in-the-loop: inject a message into the agent's next turn."""
        self.injected_messages.append(msg)

    def cancel(self):
        self.is_cancelled = True
