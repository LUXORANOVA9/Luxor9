# backend/tools/shell.py

import asyncio
import os
from tools.base import BaseTool, ToolResult

class ShellTool(BaseTool):
    name = "shell"
    description = (
        "Execute a shell command in the sandbox. "
        "Use for: installing packages, running scripts, git, file operations, "
        "system commands, etc. Returns stdout, stderr, and exit code."
    )
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute"
            }
        },
        "required": ["command"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        command = arguments.get("command", "")
        workspace = context.get("workspace_path", "/tmp")
        timeout = context.get("timeout", 120)
        
        try:
            # Execute via Docker if sandbox is active
            sandbox_id = context.get("sandbox_id")
            if sandbox_id:
                full_command = f"docker exec {sandbox_id} bash -c {self._quote(command)}"
            else:
                full_command = command
            
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Command timed out after {timeout}s"
                )
            
            stdout_str = stdout.decode('utf-8', errors='replace')[:10000]
            stderr_str = stderr.decode('utf-8', errors='replace')[:5000]
            
            exit_code = process.returncode
            
            output_parts = []
            if stdout_str.strip():
                output_parts.append(f"STDOUT:\n{stdout_str}")
            if stderr_str.strip():
                output_parts.append(f"STDERR:\n{stderr_str}")
            output_parts.append(f"EXIT CODE: {exit_code}")
            
            return ToolResult(
                success=(exit_code == 0),
                output="\n".join(output_parts),
                error=stderr_str if exit_code != 0 else None,
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Shell execution error: {str(e)}"
            )
    
    def _quote(self, cmd: str) -> str:
        """Safely quote a command for shell execution."""
        return "'" + cmd.replace("'", "'\\''") + "'"
