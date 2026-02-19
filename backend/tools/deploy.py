# backend/tools/deploy.py

import os
import subprocess
from tools.base import BaseTool, ToolResult

class DeployTool(BaseTool):
    name = "deploy"
    description = (
        "Deploy a static website or HTML file. Makes it accessible via a local URL. "
        "Use for: delivering HTML reports, dashboards, web apps to the user."
    )
    parameters = {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory containing the files to deploy (relative to workspace)"
            },
            "entry_file": {
                "type": "string",
                "description": "Entry file (default: index.html)"
            }
        },
        "required": ["directory"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        workspace = context.get("workspace_path", "/tmp")
        directory = arguments.get("directory", ".")
        entry_file = arguments.get("entry_file", "index.html")
        task_id = context.get("task_id", "default")
        
        deploy_path = os.path.join(workspace, directory)
        
        if not os.path.exists(deploy_path):
            return ToolResult(success=False, output="", error=f"Directory not found: {directory}")
        
        entry_path = os.path.join(deploy_path, entry_file)
        if not os.path.exists(entry_path):
            return ToolResult(
                success=False, output="",
                error=f"Entry file not found: {entry_file} in {directory}"
            )
        
        # For local deployment, serve via FastAPI static files
        # In production, this would deploy to a CDN
        url = f"http://localhost:8000/api/tasks/{task_id}/files/{directory}/{entry_file}"
        
        return ToolResult(
            success=True,
            output=f"Deployed! Access at:\n{url}",
            artifacts={"deployed_url": url, "entry_file": entry_file}
        )
