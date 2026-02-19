"""
FREE LLM Router — Cycles through 4 free providers:
1. Groq (Llama 3.3 70B — fastest, best quality)
2. Google Gemini 2.0 Flash (very capable)
3. Cloudflare Workers AI (Llama/Mistral)
4. Local Ollama (unlimited, runs on same VM)

Total free capacity: ~50-60 requests/minute
All with competitive quality models.
"""

import httpx
import json
import asyncio
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import os
import re

@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict[str, Any]]
    input_tokens: int
    output_tokens: int
    model: str
    provider: str
    latency_ms: int

@dataclass
class ProviderState:
    name: str
    requests_this_minute: int = 0
    minute_start: float = 0.0
    consecutive_errors: int = 0
    is_healthy: bool = True
    last_error: str = ""

class FreeLLMRouter:
    """
    Routes across multiple free LLM providers with:
    - Automatic failover
    - Rate limit tracking
    - Quality-based routing
    - Zero cost
    """

    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.cf_account = os.getenv("CF_ACCOUNT_ID", "")
        self.cf_token = os.getenv("CF_API_TOKEN", "")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

        self.providers: Dict[str, ProviderState] = {}
        self.provider_order: List[str] = []

        # Initialize available providers
        if self.groq_key:
            self.providers["groq"] = ProviderState(name="groq")
            self.provider_order.append("groq")

        if self.gemini_key:
            self.providers["gemini"] = ProviderState(name="gemini")
            self.provider_order.append("gemini")

        if self.cf_account and self.cf_token:
            self.providers["cloudflare"] = ProviderState(name="cloudflare")
            self.provider_order.append("cloudflare")

        # Ollama is always available (local)
        self.providers["ollama"] = ProviderState(name="ollama")
        self.provider_order.append("ollama")

        print(f"🧠 Free LLM providers: {self.provider_order}")

    # ═══════════════════════════════════════
    # Rate limit tracking
    # ═══════════════════════════════════════

    RATE_LIMITS = {
        "groq": 30,        # 30 requests/minute
        "gemini": 15,      # 15 requests/minute
        "cloudflare": 1200, # ~1200/min (100K/day)
        "ollama": 999,     # unlimited (local)
    }

    def _check_rate_limit(self, provider: str) -> bool:
        state = self.providers[provider]
        now = time.time()

        if now - state.minute_start > 60:
            state.requests_this_minute = 0
            state.minute_start = now

        return state.requests_this_minute < self.RATE_LIMITS.get(provider, 10)

    def _record_request(self, provider: str):
        state = self.providers[provider]
        state.requests_this_minute += 1

    # ═══════════════════════════════════════
    # Provider selection
    # ═══════════════════════════════════════

    def _select_provider(self, requires_vision: bool = False) -> str:
        """Pick the best available free provider."""
        for provider in self.provider_order:
            state = self.providers[provider]

            if not state.is_healthy and state.consecutive_errors < 5:
                state.is_healthy = True  # retry after cooldown

            if not state.is_healthy:
                continue

            if not self._check_rate_limit(provider):
                continue

            # Vision support
            if requires_vision and provider == "cloudflare":
                continue  # CF Workers AI vision is limited

            return provider

        # Fallback: always ollama (local, no limits)
        return "ollama"

    # ═══════════════════════════════════════
    # Main generate function
    # ═══════════════════════════════════════

    async def generate(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        system: str = "",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        requires_vision: bool = False,
    ) -> LLMResponse:
        """Generate with automatic provider selection and failover."""

        last_error = None

        # Try up to 3 different providers
        for attempt in range(3):
            provider = self._select_provider(requires_vision)

            try:
                start = time.time()

                if provider == "groq":
                    response = await self._call_groq(messages, tools, system, temperature, max_tokens)
                elif provider == "gemini":
                    response = await self._call_gemini(messages, tools, system, temperature, max_tokens)
                elif provider == "cloudflare":
                    response = await self._call_cloudflare(messages, tools, system, temperature, max_tokens)
                else:
                    response = await self._call_ollama(messages, tools, system, temperature, max_tokens)

                latency = int((time.time() - start) * 1000)
                response.provider = provider
                response.latency_ms = latency

                # Success — reset error counter
                self.providers[provider].consecutive_errors = 0
                self._record_request(provider)

                return response

            except Exception as e:
                last_error = str(e)
                self.providers[provider].consecutive_errors += 1
                self.providers[provider].last_error = last_error

                if self.providers[provider].consecutive_errors >= 3:
                    self.providers[provider].is_healthy = False

                # Mark rate limited
                if "429" in str(e) or "rate" in str(e).lower():
                    self.providers[provider].requests_this_minute = 999

                continue

        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    # ═══════════════════════════════════════
    # GROQ — Fastest free inference
    # ═══════════════════════════════════════

    async def _call_groq(self, messages, tools, system, temperature, max_tokens) -> LLMResponse:
        """
        Groq: FREE Llama 3.3 70B
        - 30 requests/minute
        - Insanely fast (500+ tokens/sec)
        - Best free quality
        """
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json",
        }

        groq_messages = []
        if system:
            groq_messages.append({"role": "system", "content": system})

        for msg in messages:
            groq_messages.append({
                "role": msg.get("role", "user"),
                "content": str(msg.get("content", "")),
            })

        body: Dict[str, Any] = {
            "model": "llama-3.3-70b-versatile",
            "messages": groq_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # Groq supports OpenAI-compatible tool calling
        if tools:
            body["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    }
                }
                for t in tools
            ]
            body["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=body,
            )

            if resp.status_code != 200:
                raise Exception(f"Groq {resp.status_code}: {resp.text[:200]}")

            data = resp.json()

        choice = data["choices"][0]
        content = choice["message"].get("content", "") or ""

        tool_calls = []
        if choice["message"].get("tool_calls"):
            for tc in choice["message"]["tool_calls"]:
                tool_calls.append({
                    "id": tc["id"],
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"]),
                })

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            input_tokens=data.get("usage", {}).get("prompt_tokens", 0),
            output_tokens=data.get("usage", {}).get("completion_tokens", 0),
            model="llama-3.3-70b-versatile",
            provider="groq",
            latency_ms=0,
        )

    # ═══════════════════════════════════════
    # GOOGLE GEMINI — Free & capable
    # ═══════════════════════════════════════

    async def _call_gemini(self, messages, tools, system, temperature, max_tokens) -> LLMResponse:
        """
        Google Gemini 2.0 Flash: FREE
        - 15 requests/minute
        - Supports function calling natively
        - Good at coding and reasoning
        """
        gemini_contents = []

        for msg in messages:
            role = "user" if msg.get("role") != "assistant" else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": str(msg.get("content", ""))}]
            })

        body: Dict[str, Any] = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }

        if system:
            body["systemInstruction"] = {
                "parts": [{"text": system}]
            }

        # Gemini function calling
        if tools:
            body["tools"] = [{
                "functionDeclarations": [
                    {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["parameters"],
                    }
                    for t in tools
                ]
            }]

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=body)

            if resp.status_code != 200:
                raise Exception(f"Gemini {resp.status_code}: {resp.text[:200]}")

            data = resp.json()

        # Parse response
        candidate = data.get("candidates", [{}])[0]
        parts = candidate.get("content", {}).get("parts", [])

        content = ""
        tool_calls = []

        for part in parts:
            if "text" in part:
                content += part["text"]
            elif "functionCall" in part:
                fc = part["functionCall"]
                tool_calls.append({
                    "id": f"call_{len(tool_calls)}",
                    "name": fc["name"],
                    "arguments": dict(fc.get("args", {})),
                })

        usage = data.get("usageMetadata", {})

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            model="gemini-2.0-flash",
            provider="gemini",
            latency_ms=0,
        )

    # ═══════════════════════════════════════
    # CLOUDFLARE WORKERS AI — Free backup
    # ═══════════════════════════════════════

    async def _call_cloudflare(self, messages, tools, system, temperature, max_tokens) -> LLMResponse:
        """
        Cloudflare Workers AI: FREE
        - ~100K requests/day
        - Llama 3.1 8B, Mistral 7B
        - No native tool calling → prompt-based
        """
        cf_messages = []
        if system:
            tool_prompt = self._build_tool_prompt(tools) if tools else ""
            cf_messages.append({"role": "system", "content": system + "\n\n" + tool_prompt})

        for msg in messages:
            cf_messages.append({
                "role": msg.get("role", "user"),
                "content": str(msg.get("content", "")),
            })

        url = f"https://api.cloudflare.com/client/v4/accounts/{self.cf_account}/ai/run/@cf/meta/llama-3.1-8b-instruct"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.cf_token}"},
                json={"messages": cf_messages, "max_tokens": max_tokens},
            )

            if resp.status_code != 200:
                raise Exception(f"Cloudflare {resp.status_code}: {resp.text[:200]}")

            data = resp.json()

        content = data.get("result", {}).get("response", "")
        tool_calls = self._parse_tool_calls_from_text(content) if tools else []

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            input_tokens=0,
            output_tokens=0,
            model="llama-3.1-8b-instruct",
            provider="cloudflare",
            latency_ms=0,
        )

    # ═══════════════════════════════════════
    # OLLAMA — Local, unlimited, always works
    # ═══════════════════════════════════════

    async def _call_ollama(self, messages, tools, system, temperature, max_tokens) -> LLMResponse:
        """
        Ollama: FREE, LOCAL, UNLIMITED
        - Runs on the same Oracle VM
        - qwen2.5:7b or llama3.1:8b
        - Slower than cloud but no limits
        """
        ollama_messages = []
        if system:
            tool_prompt = self._build_tool_prompt(tools) if tools else ""
            ollama_messages.append({"role": "system", "content": system + "\n\n" + tool_prompt})

        for msg in messages:
            ollama_messages.append({
                "role": msg.get("role", "user"),
                "content": str(msg.get("content", "")),
            })

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": "qwen2.5:7b",
                    "messages": ollama_messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                }
            )

            if resp.status_code != 200:
                raise Exception(f"Ollama {resp.status_code}: {resp.text[:200]}")

            data = resp.json()

        content = data.get("message", {}).get("content", "")
        tool_calls = self._parse_tool_calls_from_text(content) if tools else []

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            input_tokens=data.get("prompt_eval_count", 0),
            output_tokens=data.get("eval_count", 0),
            model="qwen2.5:7b",
            provider="ollama",
            latency_ms=0,
        )

    # ═══════════════════════════════════════
    # Embeddings (also free)
    # ═══════════════════════════════════════

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using local Ollama (free, unlimited)."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.ollama_url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text}
            )
            data = resp.json()
            return data.get("embedding", [])

    # ═══════════════════════════════════════
    # Tool calling helpers
    # ═══════════════════════════════════════

    def _build_tool_prompt(self, tools: List[Dict]) -> str:
        if not tools:
            return ""

        tool_docs = []
        for tool in tools:
            params = tool.get("parameters", {}).get("properties", {})
            param_str = ", ".join([
                f'{name}: {info.get("type", "string")}'
                for name, info in params.items()
            ])
            tool_docs.append(
                f"- {tool['name']}({param_str}): {tool['description']}"
            )

        return f"""## Tools
Use tools by responding with this EXACT format:

<tool_call>
{{"name": "tool_name", "arguments": {{"param1": "value1"}}}}
</tool_call>

ONE tool per response. Available tools:
{chr(10).join(tool_docs)}

When task is fully done, respond normally WITHOUT any tool_call tag."""

    def _parse_tool_calls_from_text(self, text: str) -> List[Dict]:
        tool_calls = []
        pattern = r'<tool_call>\s*(\{.*?\})\s*</tool_call>'
        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                tool_calls.append({
                    "id": f"call_{len(tool_calls)}",
                    "name": data.get("name", ""),
                    "arguments": data.get("arguments", {}),
                })
            except json.JSONDecodeError:
                continue

        return tool_calls

    # ═══════════════════════════════════════
    # Status
    # ═══════════════════════════════════════

    def get_status(self) -> dict:
        return {
            provider: {
                "healthy": state.is_healthy,
                "requests_this_minute": state.requests_this_minute,
                "limit": self.RATE_LIMITS.get(provider, 0),
                "errors": state.consecutive_errors,
                "last_error": state.last_error[:100] if state.last_error else None,
            }
            for provider, state in self.providers.items()
        }
