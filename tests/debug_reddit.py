"""Debug Reddit API response."""
import requests
from waflescraper.stealth import StealthConfig
s = StealthConfig()
headers = {
    "User-Agent": s.random_ua(),
    "Accept": "application/json",
}
url = "https://www.reddit.com/r/python/hot.json?limit=3"
resp = requests.get(url, headers=headers, timeout=15)
print(f"Status: {resp.status_code}")
print(f"Headers: {dict(resp.headers)}")
print(f"Body (first 500): {resp.text[:500]}")
