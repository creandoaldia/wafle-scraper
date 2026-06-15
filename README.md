```
██╗    ██╗  █████╗  ███████╗██╗     ███████╗
██║    ██║ ██╔══██╗ ██╔════╝██║     ██╔════╝
██║ █╗ ██║ ███████║ █████╗  ██║     █████╗
██║███╗██║ ██╔══██║ ██╔══╝  ██║     ██╔══╝
╚███╔███╔╝ ██║  ██║ ██║     ███████╗███████║
 ╚══╝╚══╝  ╚═╝  ╚═╝ ╚═╝     ╚══════╝╚══════╝
```

# Wafle-Scraper — Universal MCP Server for Safe Web Scraping

**Wafle-Scraper** is an MCP server that lets AI agents (OpenCode, Claude, Cursor) extract data from the web safely and responsibly.

## Safety First

| Rule | Enforcement |
|------|------------|
| **No private data** | Every browser session is **incognito** — no cookies, no localStorage, no saved passwords |
| **Only what you ask** | The scraper never mines extra data beyond your explicit request |
| **No localhost** | Internal/private IPs are blocked by default |
| **Rate limited** | Minimum 2 seconds between requests — never floods servers |
| **CAPTCHA = human only** | No automated CAPTCHA solving. If one appears, **you** solve it interactively |
| **User-Agent rotation** | Each request looks like a real browser |

## Quick Start

```bash
pip install wafle-scraper
playwright install chromium
wafle-scraper
```

## Configuration

### OpenCode / Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "wafle-scraper": {
      "command": "wafle-scraper",
      "description": "Web scraping & browser automation — incognito, audited, safe"
    }
  }
}
```

### CLI Options

```bash
wafle-scraper                    # MCP stdio mode (default for agents)
wafle-scraper --http --port 8000 # HTTP SSE mode
wafle-scraper --version          # Show version
```

## MCP Tools

| Tool | Description | Safety |
|------|-------------|--------|
| `scrape_url` | Extract text from a static URL (requests + BeautifulSoup) | ✅ Read-only, no JS |
| `scrape_browser` | Navigate a page in isolated incognito browser and extract text | ✅ Incognito, no cookies |
| `scrape_reddit` | Fetch public posts from a subreddit via official API | ✅ API, no scraping |
| `extract_emails` | Find email addresses on a public page | ✅ Only what you ask |
| `browser_interact` | Click, type, scroll, extract, screenshot in live browser | ✅ You control the actions |

## Browser Backend (Playwright)

- **Incognito always**: `storage_state=None`, fresh context per session
- **No permissions**: No camera, mic, location access
- **Anti-detection**: Rotating UA, viewport, locale, timezone
- **Natural delays**: Human-like timing between actions
- **Gradual scroll**: Loads lazy content naturally

## CAPTCHA Handling

Wafle-Scraper does **NOT** solve CAPTCHAs automatically. When a CAPTCHA is detected:

1. The scraper pauses
2. Prompts you to open the URL in your browser
3. You solve the CAPTCHA manually
4. Type `done` and the scraper continues

This is the only ethical and reliable approach without paid services.

## Security

- Blocked: `localhost`, `127.0.0.1`, private IPs, `file://`, `chrome://`
- Rate limiting (configurable, default 2s min interval)
- Scope enforcement — only processes what you explicitly request
- User-Agent rotation
- Browser isolation — Playwright contexts are fully sandboxed

## Requirements

- Python 3.10+
- Playwright with Chromium installed (`playwright install chromium`)
- Windows, macOS, Linux

## Installation from Source

```bash
git clone https://github.com/creandoaldia/wafle-scraper.git
cd wafle-scraper
pip install -e .
playwright install chromium
```

## License

MIT

## Why "Wafle-Scraper"?

Part of the **WAFLE** ecosystem (Web AI Framework for Language Ecosystems). Wafle-Scraper gives WAFLE agents the ability to read the live web — safely, transparently, and under your control.
