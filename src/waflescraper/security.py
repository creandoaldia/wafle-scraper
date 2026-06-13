"""Security enforcement — rate limiting, URL validation, scope control.

Built-in guards that prevent abuse, data leakage, and unauthorized access.
"""

import time
import re
from dataclasses import dataclass, field


@dataclass
class RateLimiter:
    min_interval: float = 2.0
    _last_call: float = 0.0

    def check(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last_call = time.time()


@dataclass
class ScopeValidator:
    blocked_patterns: list = field(default_factory=lambda: [
        r"^https?://localhost",
        r"^https?://127\.0\.0\.1",
        r"^https?://10\.\d+",
        r"^https?://192\.168\.\d+",
        r"^https?://172\.(1[6-9]|2\d|3[01])\.\d+",
        r"^file://",
        r"^chrome://",
        r"^about:",
        r"data:",
    ])
    allowed_schemes: tuple = ("http", "https")

    def assert_allowed(self, url: str):
        for pattern in self.blocked_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                raise ValueError(f"Blocked URL (internal/local): {url[:80]}")
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in self.allowed_schemes:
            raise ValueError(f"Unsupported scheme: {parsed.scheme}")
