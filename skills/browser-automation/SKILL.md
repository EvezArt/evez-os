---
name: browser-automation
description: Browser automation for web tasks. Use to navigate, fill forms, scrape data, take screenshots.
metadata:
  {
    "openclaw": {
      "emoji": "🕸️",
      "requires": { "tools": ["browser"] },
    },
  }
---

# browser-automation

Use the browser tool for web automation tasks.

## Setup

Browser is already configured. Just use it directly.

## Commands

```bash
# Open a URL
browser open <url>

# Take screenshot
browser screenshot

# Click element (use ref from snapshot)
browser act click <ref>

# Type into element
browser act type <ref> <text>

# Get page snapshot
browser snapshot
```

## Examples

- Open Amazon Associates dashboard
- Search for products
- Fill signup forms
- Scrape prices from e-commerce

## Notes

- Uses headless Chromium by default
- Profile: openclaw
- Run `browser status` to check availability