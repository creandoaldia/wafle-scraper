"""Static HTTP scraping backend — requests + BeautifulSoup.

Only fetches what the user explicitly requests. No JS, no cookies, no sessions.
"""

import re
import requests
from bs4 import BeautifulSoup
from ..stealth import StealthConfig

_stealth = StealthConfig()
_session = requests.Session()


def _get_headers() -> dict:
    return {"User-Agent": _stealth.random_ua()}


def scrape_url(url: str, extract_links: bool = False, extract_images: bool = False) -> str:
    headers = _get_headers()
    resp = _session.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    ct = (resp.headers.get("Content-Type") or "").lower()
    if "text/html" not in ct:
        return f"[Non-HTML content] Content-Type: {ct}, Size: {len(resp.content)} bytes"
    soup = BeautifulSoup(resp.text, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line for line in text.splitlines() if line.strip()]
    output = "\n".join(lines[:500])
    if extract_links:
        links = [a.get("href") for a in soup.find_all("a", href=True) if a.get("href", "").startswith("http")]
        output += "\n\n## Links\n" + "\n".join(links[:100])
    if extract_images:
        imgs = [img.get("src") for img in soup.find_all("img", src=True) if img.get("src", "").startswith("http")]
        output += "\n\n## Images\n" + "\n".join(imgs[:50])
    return output


def extract_emails_from_url(url: str) -> str:
    headers = _get_headers()
    resp = _session.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", resp.text))
    filtered = {e for e in emails if not e.endswith((".png", ".jpg", ".gif", ".css", ".js")) and "example" not in e}
    import json
    return json.dumps(sorted(filtered), indent=2)
