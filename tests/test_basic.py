"""Tests for wafle-scraper core components."""
import json
import pytest
from unittest.mock import patch, MagicMock
from waflescraper.backends.http_backend import scrape_url, extract_emails_from_url
from waflescraper.backends.reddit_backend import scrape_reddit
from waflescraper.security import ScopeValidator, RateLimiter
from waflescraper.stealth import StealthConfig


class TestStealthConfig:
    def test_random_ua_returns_string(self):
        s = StealthConfig()
        ua = s.random_ua()
        assert isinstance(ua, str)
        assert ua.startswith("Mozilla/")

    def test_random_viewport_has_keys(self):
        s = StealthConfig()
        vp = s.random_viewport()
        assert "width" in vp
        assert "height" in vp
        assert vp["width"] >= 1280

    def test_browser_launch_args_safe_by_default(self):
        s = StealthConfig()
        args = s.browser_launch_args()
        assert "--disable-web-security" not in args["args"]

    def test_browser_launch_args_unsafe_allows_web_security(self):
        s = StealthConfig()
        args = s.browser_launch_args(safe=False)
        assert "--disable-web-security" in args["args"]


class TestScopeValidator:
    def test_blocks_localhost(self):
        v = ScopeValidator()
        with pytest.raises(ValueError, match="Blocked"):
            v.assert_allowed("http://localhost/test")

    def test_blocks_private_ip(self):
        v = ScopeValidator()
        with pytest.raises(ValueError, match="Blocked"):
            v.assert_allowed("http://192.168.1.1/admin")

    def test_blocks_file_scheme(self):
        v = ScopeValidator()
        with pytest.raises(ValueError, match="Blocked"):
            v.assert_allowed("file:///etc/passwd")

    def test_allows_public_url(self):
        v = ScopeValidator()
        v.assert_allowed("https://example.com")
        v.assert_allowed("http://httpbin.org/get")

    def test_rejects_unsupported_scheme(self):
        v = ScopeValidator()
        with pytest.raises(ValueError, match="Unsupported scheme"):
            v.assert_allowed("ftp://files.example.com")


class TestRateLimiter:
    def test_sync_check_passes(self):
        rl = RateLimiter(min_interval=0.05)
        rl.check()
        rl.check()

    @pytest.mark.asyncio
    async def test_async_check_passes(self):
        rl = RateLimiter(min_interval=0.05)
        await rl.async_check()
        await rl.async_check()

    def test_enforces_min_interval(self):
        rl = RateLimiter(min_interval=0.5)
        import time
        t0 = time.time()
        rl.check()
        rl.check()
        elapsed = time.time() - t0
        assert elapsed >= 0.5

    def test_zero_interval_does_not_block(self):
        rl = RateLimiter(min_interval=0.0)
        import time
        t0 = time.time()
        rl.check()
        rl.check()
        elapsed = time.time() - t0
        assert elapsed < 0.1


class TestHttpBackend:
    @patch("waflescraper.backends.http_backend.requests.Session.get")
    def test_scrape_url_returns_text(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_resp.text = "<html><body><h1>Hello</h1><p>World</p></body></html>"
        mock_get.return_value = mock_resp
        result = scrape_url("https://example.com")
        assert "Hello" in result
        assert "World" in result

    @patch("waflescraper.backends.http_backend.requests.Session.get")
    def test_scrape_url_non_html(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/json"}
        mock_resp.content = b'{"key": "value"}'
        mock_get.return_value = mock_resp
        result = scrape_url("https://example.com/data.json")
        assert "Non-HTML content" in result

    @patch("waflescraper.backends.http_backend.requests.Session.get")
    def test_extract_emails_finds_addresses(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "Contact: user@realhost.com or admin@test.org"
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_get.return_value = mock_resp
        result = extract_emails_from_url("https://example.com")
        emails = json.loads(result)
        assert "user@realhost.com" in emails

    @patch("waflescraper.backends.http_backend.requests.Session.get")
    def test_scrape_url_timeout(self, mock_get):
        import requests
        mock_get.side_effect = requests.Timeout("timed out")
        with pytest.raises(requests.Timeout):
            scrape_url("https://example.com")


class TestRedditBackend:
    @patch("waflescraper.backends.reddit_backend.requests.get")
    def test_returns_json_from_api(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Test Post",
                            "author": "testuser",
                            "score": 42,
                            "url": "https://example.com",
                            "num_comments": 7,
                            "permalink": "/r/test/123/",
                            "over_18": False,
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_resp
        result = scrape_reddit("test", "hot", 1)
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["title"] == "Test Post"

    @patch("waflescraper.backends.reddit_backend.requests.get")
    def test_filters_nsfw(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": {
                "children": [
                    {"data": {"title": "NSFW", "over_18": True}},
                    {"data": {"title": "Safe", "over_18": False, "author": "u", "score": 1, "url": "", "num_comments": 0, "permalink": ""}},
                ]
            }
        }
        mock_get.return_value = mock_resp
        result = scrape_reddit("test", "hot", 5)
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["title"] == "Safe"
