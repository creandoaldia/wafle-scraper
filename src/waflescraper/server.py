"""wafle-scraper MCP server — safe, audited web scraping + browser automation."""

import sys
import argparse
from mcp.server.fastmcp import FastMCP

from .backends.http_backend import scrape_url as http_scrape
from .backends.browser_backend import (
    browser_navigate,
    browser_click,
    browser_extract,
    browser_screenshot,
    browser_scroll,
    browser_close,
)
from .backends.reddit_backend import scrape_reddit
from .security import RateLimiter, ScopeValidator
from .stealth import StealthConfig
from .captcha_handler import CaptchaHandler

mcp = FastMCP("wafle-scraper", description=__import__("__init__", fromlist=["__description__"]).__description__)

_limiter = RateLimiter()
_validator = ScopeValidator()
_stealth = StealthConfig()
_captcha = CaptchaHandler()


@mcp.tool()
def scrape_url(url: str, extract_links: bool = False, extract_images: bool = False) -> str:
    """Extract readable text content from a static URL.

    Args:
        url: Full URL to scrape (http/https).
        extract_links: If True, include hyperlinks in output.
        extract_images: If True, include image URLs in output.

    Returns:
        Markdown-formatted content extracted from the page.
    """
    _limiter.check()
    _validator.assert_allowed(url)
    result = http_scrape(url, extract_links, extract_images)
    return result


@mcp.tool()
def scrape_browser(url: str, wait_selector: str = "", scroll: bool = False) -> str:
    """Navigate a page in an isolated incognito browser and extract text.

    Args:
        url: Full URL to navigate to.
        wait_selector: Optional CSS selector to wait for (dynamic content).
        scroll: If True, gradually scroll to load lazy content.

    Returns:
        Markdown-formatted text content from the rendered page.
    """
    _limiter.check()
    _validator.assert_allowed(url)
    _captcha.check_interactive()
    result = browser_navigate(url, wait_selector, scroll)
    return result


@mcp.tool()
def scrape_reddit(subreddit: str, sort: str = "hot", limit: int = 10) -> str:
    """Fetch public posts from a subreddit via the official Reddit API.

    Args:
        subreddit: Name of the subreddit (without r/).
        sort: One of 'hot', 'new', 'top', 'rising'.
        limit: Number of posts to fetch (1-100).

    Returns:
        Markdown-formatted list of posts with title, author, score, and URL.
    """
    _limiter.check()
    return scrape_reddit(subreddit, sort, limit)


@mcp.tool()
def extract_emails(url: str) -> str:
    """Find email addresses on a public page.

    Args:
        url: Full URL to scan.

    Returns:
        JSON list of found email addresses.
    """
    _limiter.check()
    _validator.assert_allowed(url)
    from .backends.http_backend import extract_emails_from_url
    result = extract_emails_from_url(url)
    return result


@mcp.tool()
def browser_interact(action: str, selector: str = "", value: str = "") -> str:
    """Interact with the active browser page (click, type, extract).

    Args:
        action: One of 'click', 'type', 'extract', 'scroll', 'screenshot'.
        selector: CSS selector for the target element.
        value: Text value for 'type' action.

    Returns:
        Result of the interaction.
    """
    _captcha.check_interactive()
    if action == "click":
        return browser_click(selector)
    elif action == "type":
        return browser_interact_type(selector, value)
    elif action == "extract":
        return browser_extract(selector)
    elif action == "screenshot":
        return browser_screenshot()
    elif action == "scroll":
        return browser_scroll()
    elif action == "close":
        return browser_close()
    return f"Unknown action: {action}"


def main():
    parser = argparse.ArgumentParser(description="wafle-scraper MCP server")
    parser.add_argument("--http", action="store_true", help="Run in HTTP SSE mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP mode")
    parser.add_argument("--version", action="version", version=f"wafle-scraper {__import__('__init__', fromlist=['__version__']).__version__}")
    args = parser.parse_args()

    if args.http:
        mcp.run(transport="sse", host="0.0.0.0", port=args.port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
