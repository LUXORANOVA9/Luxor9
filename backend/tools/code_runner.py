# backend/tools/code_runner.py

import asyncio
import os
import tempfile
from tools.base import BaseTool, ToolResult

class PythonRunTool(BaseTool):
    name = "python_run"
    description = (
        "Execute a Python script. The script is saved to a file and executed. "
        "Use for: data analysis, calculations, generating charts, processing files. "
        "All packages from the sandbox are available (pandas, matplotlib, etc.)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            },
            "filename": {
                "type": "string",
                "description": "Optional filename to save script as (default: script.py)"
            }
        },
        "required": ["code"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        code = arguments.get("code", "")
        filename = arguments.get("filename", "script.py")
        workspace = context.get("workspace_path", "/tmp")
        
        # Save script to workspace
        script_path = os.path.join(workspace, filename)
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(code)
        
        # Execute
        try:
            process = await asyncio.create_subprocess_exec(
                "python3", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=120
            )
            
            stdout_str = stdout.decode('utf-8', errors='replace')[:8000]
            stderr_str = stderr.decode('utf-8', errors='replace')[:4000]
            
            output_parts = [f"Saved and executed: {filename}"]
            if stdout_str.strip():
                output_parts.append(f"\nOutput:\n{stdout_str}")
            if stderr_str.strip() and process.returncode != 0:
                output_parts.append(f"\nErrors:\n{stderr_str}")
            output_parts.append(f"\nExit code: {process.returncode}")
            
            return ToolResult(
                success=(process.returncode == 0),
                output="\n".join(output_parts),
                error=stderr_str if process.returncode != 0 else None,
            )
        except asyncio.TimeoutError:
            return ToolResult(success=False, output="", error="Script timed out after 120s")
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
