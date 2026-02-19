# backend/tools/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class ToolResult:
    success: bool
    output: str
    error: Optional[str] = None
    artifacts: Dict[str, Any] = field(default_factory=dict)
    # artifacts can include: screenshot_base64, file_paths, urls, etc.

class BaseTool(ABC):
    """Base class for all Luxor9 tools."""
    
    name: str
    description: str
    parameters: dict  # JSON Schema
    
    @abstractmethod
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        """Execute the tool with given arguments."""
        pass
    
    def to_schema(self) -> dict:
        """Convert to LLM tool schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


def get_all_tools() -> List[BaseTool]:
    """Get all available tools."""
    from tools.shell import ShellTool
    from tools.filesystem import FileReadTool, FileWriteTool, FileListTool
    from tools.browser import BrowserNavigateTool, BrowserClickTool, BrowserTypeTool, BrowserScreenshotTool, BrowserScrollTool
    from tools.search import WebSearchTool
    from tools.code_runner import PythonRunTool
    from tools.deploy import DeployTool
    
    return [
        ShellTool(),
        FileReadTool(),
        FileWriteTool(),
        FileListTool(),
        BrowserNavigateTool(),
        BrowserClickTool(),
        BrowserTypeTool(),
        BrowserScreenshotTool(),
        BrowserScrollTool(),
        WebSearchTool(),
        PythonRunTool(),
        DeployTool(),
    ]
