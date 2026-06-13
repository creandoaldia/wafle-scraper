"""CAPTCHA handler — human-in-the-loop interactive resolution.

When a CAPTCHA is detected, the scraper pauses and prompts the user
to solve it manually. No automated CAPTCHA solving.
"""

import sys
import json
import time


class CaptchaDetected(Exception):
    pass


class CaptchaHandler:
    def __init__(self):
        self._interactive = True

    def check_interactive(self):
        pass

    def prompt_user(self, page_source: str = "") -> str:
        print("\n" + "=" * 60)
        print("  CAPTCHA DETECTED")
        print("=" * 60)
        print("  The page is showing a CAPTCHA or access challenge.")
        print("  To continue, please:")
        print("    1. Open the URL in your regular browser")
        print("    2. Complete the CAPTCHA")
        print("    3. Type 'done' here when finished")
        print("  Or type 'skip' to abort this request.")
        print("=" * 60)
        while True:
            try:
                response = input("  > ").strip().lower()
                if response == "done":
                    return "resolved"
                elif response == "skip":
                    return "skipped"
                else:
                    print("  Type 'done' or 'skip'.")
            except (EOFError, KeyboardInterrupt):
                return "skipped"
