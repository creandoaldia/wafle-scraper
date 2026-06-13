"""Reddit public data — uses old.reddit.com for anonymous access when JSON API is blocked."""

import json
import requests
from bs4 import BeautifulSoup
from ..stealth import StealthConfig

_stealth = StealthConfig()


def scrape_reddit(subreddit: str, sort: str = "hot", limit: int = 10) -> str:
    if sort not in ("hot", "new", "top", "rising"):
        sort = "hot"
    limit = max(1, min(100, limit))
    headers = {"User-Agent": _stealth.random_ua(), "Accept": "application/json"}
    api_url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}"
    resp = requests.get(api_url, headers=headers, timeout=15)
    if resp.status_code == 200:
        try:
            data = resp.json()
            posts = []
            for child in data.get("data", {}).get("children", []):
                d = child.get("data", {})
                if d.get("over_18"):
                    continue
                posts.append({
                    "title": d.get("title", ""),
                    "author": d.get("author", "[deleted]"),
                    "score": d.get("score", 0),
                    "url": d.get("url", ""),
                    "comments": d.get("num_comments", 0),
                    "permalink": "https://reddit.com" + (d.get("permalink") or ""),
                })
            return json.dumps(posts, indent=2)
        except (json.JSONDecodeError, KeyError):
            pass
    html_headers = {"User-Agent": _stealth.random_ua()}
    html_url = f"https://old.reddit.com/r/{subreddit}/{sort}/?limit={limit}"
    html_resp = requests.get(html_url, headers=html_headers, timeout=15)
    if html_resp.status_code != 200:
        msg = f"[Reddit blocked this request (HTTP {resp.status_code}). "
        msg += "Use scrape_browser with old.reddit.com for anonymous access.]"
        return json.dumps({"error": msg})
    soup = BeautifulSoup(html_resp.text, "lxml")
    posts = []
    for entry in soup.select("div.thing")[:limit]:
        title_el = entry.select_one("a.title")
        if not title_el:
            continue
        author_el = entry.select_one("a.author")
        score_el = entry.select_one("div.score.unvoted")
        comments_el = entry.select_one("a.comments")
        posts.append({
            "title": title_el.text.strip(),
            "author": author_el.text.strip() if author_el else "[deleted]",
            "score": score_el.text.strip() if score_el else "0",
            "url": title_el.get("href", ""),
            "comments": comments_el.text.strip() if comments_el else "0",
        })
    return json.dumps(posts, indent=2)
