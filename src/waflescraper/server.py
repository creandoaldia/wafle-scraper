"""wafle-scraper MCP server — safe, audited web scraping + browser automation."""
import sys
import argparse
from mcp.server.fastmcp import FastMCP
import anyio

from .backends.http_backend import scrape_url as http_scrape
from .backends.browser_backend import (
    browser_navigate, browser_click, browser_interact_type,
    browser_extract, browser_screenshot, browser_scroll, browser_close,
)
from .backends.reddit_backend import scrape_reddit as _scrape_reddit_backend
from .security import RateLimiter, ScopeValidator
from .stealth import StealthConfig
from .captcha_handler import CaptchaHandler
from . import __version__, __description__

mcp = FastMCP("wafle-scraper")
_limiter = RateLimiter()
_validator = ScopeValidator()
_stealth = StealthConfig()
_captcha = CaptchaHandler()


@mcp.tool()
def scrape_url(url: str, extract_links: bool = False, extract_images: bool = False) -> str:
    """Extract readable text content from a static URL."""
    _limiter.check()
    _validator.assert_allowed(url)
    return http_scrape(url, extract_links, extract_images)


@mcp.tool()
async def scrape_browser(url: str, wait_selector: str = "", scroll: bool = False) -> str:
    """Navigate a page in an isolated incognito browser and extract text."""
    _limiter.check()
    _validator.assert_allowed(url)
    _captcha.check_interactive()
    def _run():
        return browser_navigate(url, wait_selector, scroll)
    return await anyio.to_thread.run_sync(_run)


@mcp.tool()
def scrape_reddit(subreddit: str, sort: str = "hot", limit: int = 10) -> str:
    """Fetch public posts from a subreddit via the official Reddit API."""
    _limiter.check()
    return _scrape_reddit_backend(subreddit, sort, limit)


@mcp.tool()
def extract_emails(url: str) -> str:
    """Find email addresses on a public page."""
    _limiter.check()
    _validator.assert_allowed(url)
    from .backends.http_backend import extract_emails_from_url
    return extract_emails_from_url(url)


@mcp.tool()
async def browser_interact(action: str, selector: str = "", value: str = "") -> str:
    """Interact with the active browser page (click, type, extract)."""
    _captcha.check_interactive()
    def _run():
        actions = {
            "click": lambda: browser_click(selector),
            "type": lambda: browser_interact_type(selector, value),
            "extract": lambda: browser_extract(selector),
            "screenshot": lambda: browser_screenshot(),
            "scroll": lambda: browser_scroll(),
            "close": lambda: browser_close(),
        }
        fn = actions.get(action)
        return fn() if fn else f"Unknown action: {action}"
    return await anyio.to_thread.run_sync(_run)


def main():
    parser = argparse.ArgumentParser(description="wafle-scraper MCP server")
    parser.add_argument("--http", action="store_true", help="Run in HTTP SSE mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP mode")
    parser.add_argument("--version", action="version", version=f"wafle-scraper {__version__}")
    args = parser.parse_args()
    if args.http:
        mcp.run(transport="sse", host="0.0.0.0", port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
