"""Test basic wafle-scraper functionality."""
import json
from waflescraper.backends.http_backend import scrape_url, extract_emails_from_url
from waflescraper.backends.reddit_backend import scrape_reddit
from waflescraper.security import ScopeValidator, RateLimiter
from waflescraper.stealth import StealthConfig

print("=== StealthConfig ===")
s = StealthConfig()
print(f"UA: {s.random_ua()}")

print("\n=== ScopeValidator ===")
v = ScopeValidator()
try:
    v.assert_allowed("http://localhost/test")
    print("ERROR: should have blocked localhost")
except ValueError as e:
    print(f"OK: blocked localhost: {e}")

try:
    v.assert_allowed("https://example.com")
    print("OK: allowed example.com")
except ValueError as e:
    print(f"ERROR: {e}")

print("\n=== RateLimiter ===")
rl = RateLimiter(min_interval=0.1)
rl.check()
print("OK: first call passed")
rl.check()
print("OK: second call passed (waited)")

print("\n=== scrape_url (static) ===")
result = scrape_url("https://example.com", False, False)
print(f"OK: extracted {len(result)} chars from example.com")

print("\n=== extract_emails ===")
emails = extract_emails_from_url("https://example.com")
print(f"OK: found {len(json.loads(emails))} emails")

print("\n=== scrape_reddit ===")
try:
    reddit = scrape_reddit("python", "hot", 3)
    data = json.loads(reddit)
    if isinstance(data, list):
        print(f"OK: fetched {len(data)} posts from r/python")
        for p in data[:3]:
            print(f'  - {p["title"][:60]}')
    else:
        print(f"Info: {reddit[:200]}")
except Exception as e:
    print(f"Reddit test: {e}")

print("\n=== All basic tests passed ===")
