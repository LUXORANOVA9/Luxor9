# backend/tools/search.py

import httpx
from tools.base import BaseTool, ToolResult

class WebSearchTool(BaseTool):
    name = "web_search"
    description = (
        "Search the web for information. Returns titles, URLs, and snippets. "
        "Use when you need current information, facts, or to find resources. "
        "Uses DuckDuckGo (free, no API key needed)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results (default: 8)"
            }
        },
        "required": ["query"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        query = arguments.get("query", "")
        num_results = arguments.get("num_results", 8)
        
        try:
            results = await self._ddg_search(query, num_results)
            
            if not results:
                return ToolResult(
                    success=True,
                    output="No results found. Try a different query."
                )
            
            output_lines = [f"Search results for: \"{query}\"\n"]
            for i, r in enumerate(results, 1):
                output_lines.append(
                    f"{i}. {r['title']}\n"
                    f"   URL: {r['url']}\n"
                    f"   {r['snippet']}\n"
                )
            
            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                artifacts={"results": results}
            )
        except Exception as e:
            return ToolResult(
                success=False, output="",
                error=f"Search error: {str(e)}"
            )
    
    async def _ddg_search(self, query: str, num_results: int) -> list:
        """Search using DuckDuckGo HTML (no API key needed)."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                },
                follow_redirects=True,
            )
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.select('.result'):
                title_el = result.select_one('.result__title a')
                snippet_el = result.select_one('.result__snippet')
                
                if title_el:
                    title = title_el.get_text(strip=True)
                    url = title_el.get('href', '')
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                    
                    # DuckDuckGo redirects through their URL
                    if 'uddg=' in url:
                        from urllib.parse import unquote, parse_qs, urlparse
                        parsed = urlparse(url)
                        params = parse_qs(parsed.query)
                        if 'uddg' in params:
                            url = unquote(params['uddg'][0])
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet[:200]
                    })
                    
                    if len(results) >= num_results:
                        break
            
            return results
