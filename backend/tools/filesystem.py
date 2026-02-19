# backend/tools/filesystem.py

import os
import aiofiles
from pathlib import Path
from tools.base import BaseTool, ToolResult

class FileWriteTool(BaseTool):
    name = "file_write"
    description = (
        "Write content to a file. Creates the file if it doesn't exist. "
        "Creates parent directories automatically. "
        "Use for: creating scripts, saving data, writing reports, todo.md, etc."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path relative to workspace (e.g., 'src/app.py', 'todo.md')"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            }
        },
        "required": ["path", "content"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        workspace = context.get("workspace_path", "/tmp")
        rel_path = arguments.get("path", "")
        content = arguments.get("content", "")
        
        # Security: prevent path traversal
        full_path = os.path.normpath(os.path.join(workspace, rel_path))
        if not full_path.startswith(os.path.normpath(workspace)):
            return ToolResult(
                success=False, output="",
                error="Path traversal not allowed"
            )
        
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            async with aiofiles.open(full_path, 'w') as f:
                await f.write(content)
            
            size = os.path.getsize(full_path)
            return ToolResult(
                success=True,
                output=f"Written {size} bytes to {rel_path}",
                artifacts={"file_path": rel_path, "size": size}
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class FileReadTool(BaseTool):
    name = "file_read"
    description = (
        "Read content from a file. "
        "Use for: reading data files, checking code, reviewing outputs."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path relative to workspace"
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum lines to read (default: 200). Use for large files.",
            }
        },
        "required": ["path"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        workspace = context.get("workspace_path", "/tmp")
        rel_path = arguments.get("path", "")
        max_lines = arguments.get("max_lines", 200)
        
        full_path = os.path.normpath(os.path.join(workspace, rel_path))
        if not full_path.startswith(os.path.normpath(workspace)):
            return ToolResult(success=False, output="", error="Path traversal not allowed")
        
        if not os.path.exists(full_path):
            return ToolResult(success=False, output="", error=f"File not found: {rel_path}")
        
        try:
            async with aiofiles.open(full_path, 'r', errors='replace') as f:
                lines = await f.readlines()
            
            total_lines = len(lines)
            if total_lines > max_lines:
                content = "".join(lines[:max_lines])
                content += f"\n\n... ({total_lines - max_lines} more lines truncated)"
            else:
                content = "".join(lines)
            
            return ToolResult(
                success=True,
                output=content,
                artifacts={"total_lines": total_lines}
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

class FileListTool(BaseTool):
    name = "file_list"
    description = (
        "List files and directories in the workspace. "
        "Use for: exploring workspace structure, finding files."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path relative to workspace (default: root)"
            }
        },
        "required": []
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        workspace = context.get("workspace_path", "/tmp")
        rel_path = arguments.get("path", ".")
        
        full_path = os.path.normpath(os.path.join(workspace, rel_path))
        if not full_path.startswith(os.path.normpath(workspace)):
            return ToolResult(success=False, output="", error="Path traversal not allowed")
        
        if not os.path.exists(full_path):
            return ToolResult(success=False, output="", error=f"Directory not found: {rel_path}")
        
        try:
            entries = []
            for item in sorted(os.listdir(full_path)):
                item_path = os.path.join(full_path, item)
                if os.path.isdir(item_path):
                    entries.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(item_path)
                    entries.append(f"📄 {item} ({self._format_size(size)})")
            
            if not entries:
                return ToolResult(success=True, output="(empty directory)")
            
            return ToolResult(success=True, output="\n".join(entries))
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
    
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
