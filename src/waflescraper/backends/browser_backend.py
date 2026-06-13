"""Browser automation backend — Playwright in isolated incognito mode.

EVERY navigation creates a fresh isolated context:
- No cookies, no localStorage, no session persistence
- No saved passwords, no autofill
- Rotating User-Agent
- Optional stealth for anti-detection
"""

import time
import random
from playwright.sync_api import sync_playwright
from ..stealth import StealthConfig

_stealth = StealthConfig()
_playwright = None
_browser = None
_context = None
_page = None


def _ensure_browser():
    global _playwright, _browser, _context, _page
    if _browser is None or not _browser.is_connected():
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(
            headless=True,
            args=[
                "--incognito",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
    if _context is None:
        _context = _browser.new_context(
            storage_state=None,
            no_viewport=False,
            user_agent=_stealth.random_ua(),
            locale="en-US",
            timezone_id="America/New_York",
            permissions=[],
            ignore_https_errors=False,
        )
        _page = _context.new_page()
        _page.set_default_timeout(30000)


def _cleanup_context():
    global _context, _page
    if _page:
        try:
            _page.close()
        except Exception:
            pass
        _page = None
    if _context:
        try:
            _context.close()
        except Exception:
            pass
        _context = None


def _human_delay(min_s: float = 0.5, max_s: float = 2.0):
    time.sleep(random.uniform(min_s, max_s))


def _gradual_scroll(page, steps: int = 8):
    height = page.evaluate("document.body.scrollHeight")
    for i in range(1, steps + 1):
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {i / steps})")
        _human_delay(0.3, 0.8)


def browser_navigate(url: str, wait_selector: str = "", scroll: bool = False) -> str:
    _cleanup_context()
    _ensure_browser()
    _human_delay()
    _page.goto(url, wait_until="networkidle", timeout=45000)
    _human_delay(0.5, 1.5)
    if wait_selector:
        _page.wait_for_selector(wait_selector, timeout=10000)
    if scroll:
        _gradual_scroll(_page)
        _human_delay()
    title = _page.title()
    body = _page.inner_text("body") or ""
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    text = "\n".join(lines[:500])
    return f"# {title}\n\n{text}"


def browser_click(selector: str) -> str:
    _ensure_browser()
    _human_delay()
    el = _page.wait_for_selector(selector, timeout=10000)
    if el:
        el.click()
        _human_delay()
        return f"Clicked: {selector}"
    return f"Element not found: {selector}"


def browser_extract(selector: str) -> str:
    _ensure_browser()
    els = _page.query_selector_all(selector)
    if not els:
        return f"No elements found for: {selector}"
    results = []
    for el in els[:100]:
        text = el.inner_text()
        if text.strip():
            results.append(text.strip())
    return "\n---\n".join(results) if results else "(empty elements)"


def browser_screenshot() -> str:
    _ensure_browser()
    path = f"wafle_scraper_screenshot_{int(time.time())}.png"
    _page.screenshot(path=path, full_page=True)
    return f"Screenshot saved: {path}"


def browser_scroll() -> str:
    _ensure_browser()
    _gradual_scroll(_page)
    return "Scrolled to bottom"


def browser_close() -> str:
    global _page, _context, _browser, _playwright
    _cleanup_context()
    if _browser:
        try:
            _browser.close()
        except Exception:
            pass
        _browser = None
    if _playwright:
        try:
            _playwright.stop()
        except Exception:
            pass
        _playwright = None
    return "Browser closed"


def browser_interact_type(selector: str, value: str) -> str:
    _ensure_browser()
    _human_delay()
    el = _page.wait_for_selector(selector, timeout=10000)
    if el:
        el.click()
        _human_delay(0.1, 0.3)
        for ch in value:
            _page.keyboard.type(ch, delay=random.randint(30, 120))
            _human_delay(0.01, 0.05)
        return f"Typed into: {selector}"
    return f"Element not found: {selector}"
