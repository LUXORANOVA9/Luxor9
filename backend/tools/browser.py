# backend/tools/browser.py

import asyncio
import base64
import json
from typing import Optional
from tools.base import BaseTool, ToolResult

# Global browser session per task
_browser_sessions = {}

async def get_browser_session(task_id: str):
    """Get or create a Playwright browser session for a task."""
    if task_id not in _browser_sessions:
        from playwright.async_api import async_playwright
        
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        _browser_sessions[task_id] = {
            'pw': pw,
            'browser': browser,
            'context': context,
            'page': page,
        }
    
    return _browser_sessions[task_id]

async def close_browser_session(task_id: str):
    if task_id in _browser_sessions:
        session = _browser_sessions[task_id]
        await session['browser'].close()
        await session['pw'].stop()
        del _browser_sessions[task_id]

async def _extract_page_info(page) -> dict:
    """Extract interactive elements and page text from current page."""
    try:
        elements = await page.evaluate("""
        () => {
            const selectors = 'a[href], button, input, select, textarea, [role="button"], [onclick]';
            const els = document.querySelectorAll(selectors);
            const results = [];
            let idx = 0;
            
            for (const el of els) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0 && 
                    rect.top < window.innerHeight && rect.bottom > 0 &&
                    rect.left < window.innerWidth && rect.right > 0) {
                    results.push({
                        index: idx++,
                        tag: el.tagName.toLowerCase(),
                        text: (el.textContent || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim().substring(0, 80),
                        type: el.type || '',
                        href: el.href || '',
                        bbox: {
                            x: Math.round(rect.x + rect.width/2),
                            y: Math.round(rect.y + rect.height/2)
                        }
                    });
                }
            }
            return results.slice(0, 50);
        }
        """)
    except Exception:
        elements = []
    
    try:
        page_text = await page.evaluate("""
        () => {
            return document.body ? document.body.innerText.substring(0, 3000) : '';
        }
        """)
    except Exception:
        page_text = ""
    
    return {
        "url": page.url,
        "title": await page.title(),
        "interactive_elements": elements,
        "page_text": page_text,
    }


class BrowserNavigateTool(BaseTool):
    name = "browser_navigate"
    description = (
        "Navigate the browser to a URL. Returns page info and screenshot. "
        "Use for: visiting websites, opening pages."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to navigate to"
            }
        },
        "required": ["url"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        task_id = context.get("task_id", "default")
        url = arguments.get("url", "")
        
        try:
            session = await get_browser_session(task_id)
            page = session['page']
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Get page info
            info = await _extract_page_info(page)
            
            # Take screenshot
            screenshot = await page.screenshot(type='png')
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            # Format elements for LLM
            elements_str = "\n".join([
                f"  [{el['index']}] <{el['tag']}> \"{el['text'][:50]}\" {el.get('href', '')[:60]}"
                for el in info["interactive_elements"][:30]
            ])
            
            output = (
                f"Navigated to: {info['url']}\n"
                f"Title: {info['title']}\n\n"
                f"Interactive Elements:\n{elements_str}\n\n"
                f"Page Text Preview:\n{info['page_text'][:1500]}"
            )
            
            return ToolResult(
                success=True,
                output=output,
                artifacts={"screenshot": screenshot_b64, "page_info": info}
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Browser error: {str(e)}")


class BrowserClickTool(BaseTool):
    name = "browser_click"
    description = (
        "Click an interactive element on the page by its index number. "
        "First use browser_navigate or browser_screenshot to see available elements. "
        "Elements are listed as [index] <tag> \"text\"."
    )
    parameters = {
        "type": "object",
        "properties": {
            "element_index": {
                "type": "integer",
                "description": "Index number of the element to click (from the elements list)"
            }
        },
        "required": ["element_index"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        task_id = context.get("task_id", "default")
        element_index = arguments.get("element_index", 0)
        
        try:
            session = await get_browser_session(task_id)
            page = session['page']
            
            # Get current elements to find coordinates
            info = await _extract_page_info(page)
            elements = info["interactive_elements"]
            
            target = None
            for el in elements:
                if el["index"] == element_index:
                    target = el
                    break
            
            if not target:
                return ToolResult(
                    success=False, output="",
                    error=f"Element [{element_index}] not found. Available: 0-{len(elements)-1}"
                )
            
            # Click at element center
            await page.mouse.click(target["bbox"]["x"], target["bbox"]["y"])
            await page.wait_for_timeout(2000)
            
            # Get updated page info
            new_info = await _extract_page_info(page)
            screenshot = await page.screenshot(type='png')
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            elements_str = "\n".join([
                f"  [{el['index']}] <{el['tag']}> \"{el['text'][:50]}\""
                for el in new_info["interactive_elements"][:30]
            ])
            
            output = (
                f"Clicked element [{element_index}]: <{target['tag']}> \"{target['text'][:50]}\"\n"
                f"Current URL: {new_info['url']}\n"
                f"Title: {new_info['title']}\n\n"
                f"Interactive Elements:\n{elements_str}\n\n"
                f"Page Text Preview:\n{new_info['page_text'][:1500]}"
            )
            
            return ToolResult(
                success=True,
                output=output,
                artifacts={"screenshot": screenshot_b64, "page_info": new_info}
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Click error: {str(e)}")


class BrowserTypeTool(BaseTool):
    name = "browser_type"
    description = (
        "Type text into the currently focused element or a specific element. "
        "Click on an input element first, then type."
    )
    parameters = {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to type"
            },
            "element_index": {
                "type": "integer",
                "description": "Optional: click this element first before typing"
            },
            "press_enter": {
                "type": "boolean",
                "description": "Press Enter after typing (for search forms)"
            }
        },
        "required": ["text"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        task_id = context.get("task_id", "default")
        text = arguments.get("text", "")
        element_index = arguments.get("element_index")
        press_enter = arguments.get("press_enter", False)
        
        try:
            session = await get_browser_session(task_id)
            page = session['page']
            
            if element_index is not None:
                info = await _extract_page_info(page)
                for el in info["interactive_elements"]:
                    if el["index"] == element_index:
                        await page.mouse.click(el["bbox"]["x"], el["bbox"]["y"])
                        await page.wait_for_timeout(500)
                        # Clear existing text
                        await page.keyboard.press("Control+a")
                        await page.keyboard.press("Backspace")
                        break
            
            await page.keyboard.type(text, delay=30)
            
            if press_enter:
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(2000)
            
            info = await _extract_page_info(page)
            screenshot = await page.screenshot(type='png')
            
            return ToolResult(
                success=True,
                output=f"Typed: \"{text[:100]}\"" + (" + Enter" if press_enter else "") + f"\nCurrent URL: {info['url']}",
                artifacts={"screenshot": base64.b64encode(screenshot).decode()}
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class BrowserScreenshotTool(BaseTool):
    name = "browser_screenshot"
    description = (
        "Take a screenshot of the current page and get page info. "
        "Use when you need to see the current state of the page."
    )
    parameters = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        task_id = context.get("task_id", "default")
        
        try:
            session = await get_browser_session(task_id)
            page = session['page']
            
            info = await _extract_page_info(page)
            screenshot = await page.screenshot(type='png')
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            elements_str = "\n".join([
                f"  [{el['index']}] <{el['tag']}> \"{el['text'][:50]}\""
                for el in info["interactive_elements"][:30]
            ])
            
            output = (
                f"URL: {info['url']}\n"
                f"Title: {info['title']}\n\n"
                f"Interactive Elements:\n{elements_str}\n\n"
                f"Page Text:\n{info['page_text'][:2000]}"
            )
            
            return ToolResult(
                success=True,
                output=output,
                artifacts={"screenshot": screenshot_b64, "page_info": info}
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


class BrowserScrollTool(BaseTool):
    name = "browser_scroll"
    description = "Scroll the page up or down to see more content."
    parameters = {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "enum": ["up", "down"],
                "description": "Direction to scroll"
            }
        },
        "required": ["direction"]
    }
    
    async def execute(self, arguments: dict, context: dict) -> ToolResult:
        task_id = context.get("task_id", "default")
        direction = arguments.get("direction", "down")
        
        try:
            session = await get_browser_session(task_id)
            page = session['page']
            
            delta = -500 if direction == "up" else 500
            await page.mouse.wheel(0, delta)
            await page.wait_for_timeout(1000)
            
            info = await _extract_page_info(page)
            screenshot = await page.screenshot(type='png')
            
            return ToolResult(
                success=True,
                output=f"Scrolled {direction}.\nPage text:\n{info['page_text'][:2000]}",
                artifacts={"screenshot": base64.b64encode(screenshot).decode()}
            )
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))
