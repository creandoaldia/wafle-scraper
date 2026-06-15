"""Stealth configuration — anti-detection and human-like behavior.

Rotating User-Agents, viewport randomization, natural timing delays,
browser fingerprint evasion, and behavioral patterns that avoid bot detection.
All values are realistic and based on actual browser usage patterns.
"""

import random
import time


_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.0",
]

_VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1440, "height": 900},
    {"width": 1680, "height": 1050},
    {"width": 1280, "height": 720},
]

_LOCALES = ["en-US", "en-GB", "en-CA", "en-AU", "es-ES", "es-MX"]
_TIMEZONES = [
    "America/New_York", "America/Chicago", "America/Denver",
    "America/Los_Angeles", "Europe/Madrid", "Europe/London",
    "Australia/Sydney", "Asia/Tokyo",
]


class StealthConfig:
    """Anti-detection configuration with human-like behavior patterns."""

    def random_ua(self) -> str:
        return random.choice(_USER_AGENTS)

    def random_viewport(self) -> dict:
        return random.choice(_VIEWPORTS)

    def random_locale(self) -> str:
        return random.choice(_LOCALES)

    def random_timezone(self) -> str:
        return random.choice(_TIMEZONES)

    @staticmethod
    def human_delay(min_s: float = 0.5, max_s: float = 2.0):
        """Sleep for a random duration simulating human reaction time."""
        time.sleep(random.uniform(min_s, max_s))

    @staticmethod
    def variable_delay(base: float = 1.0, jitter: float = 0.5):
        """Sleep for base ± jitter seconds."""
        time.sleep(max(0.1, base + random.uniform(-jitter, jitter)))

    @staticmethod
    def typing_delay() -> float:
        return random.uniform(0.03, 0.12)

    @staticmethod
    def mouse_path_delay() -> float:
        return random.uniform(0.1, 0.4)

    @staticmethod
    def page_load_delay() -> float:
        return random.uniform(1.0, 3.0)

    def browser_launch_args(self) -> dict:
        """Extra args for undetected browser launch."""
        return {
            "args": [
                "--incognito",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-web-security",
                "--disable-features=ChromeWhatsNewUI",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-search-engine-choice-screen",
                "--mute-audio",
            ]
        }

    def context_params(self) -> dict:
        return {
            "no_viewport": False,
            "user_agent": self.random_ua(),
            "locale": self.random_locale(),
            "timezone_id": self.random_timezone(),
            "permissions": [],
            "ignore_https_errors": False,
            "viewport": self.random_viewport(),
        }
