# Playwright Setup for Patent Scraping

## Overview

The patent API sources now use **Playwright** for browser automation to handle JavaScript-heavy sites like Google Patents and USPTO Patent Public Search.

## Why Playwright?

- **Handles JavaScript**: Both Google Patents and USPTO require JavaScript to render content
- **Modern & Fast**: Better performance than Selenium
- **Async Support**: Works seamlessly with Python's async/await
- **Headless Mode**: Runs browsers in background (no GUI needed)

## Installation

### Step 1: Install Python Package
```bash
pip install playwright
```

### Step 2: Install Browser
```bash
playwright install chromium
```

Or use the provided script:
```bash
./install_playwright.sh
```

## How It Works

### Google Patents
1. Launches headless Chromium browser
2. Navigates to Google Patents search page
3. Waits for JavaScript to render results
4. Extracts patent numbers, titles, dates from rendered HTML
5. Returns structured patent data

### USPTO Patent Public Search
1. Launches headless Chromium browser
2. Navigates to USPTO search interface
3. Fills in search form with drug name/indication
4. Clicks search button
5. Waits for results to load
6. Extracts patent data from rendered page

## Performance

- **First run**: May be slower (browser startup)
- **Subsequent runs**: Faster (browser reuse)
- **Timeout**: 30 seconds per source
- **Rate limiting**: 1-2 second delays between requests

## Troubleshooting

### Browser not found
```bash
playwright install chromium
```

### Permission errors
```bash
# On Linux/Mac, you may need:
sudo playwright install chromium
```

### Timeout errors
- Increase timeout in code if needed
- Check internet connection
- Some sites may block automated browsers

## Testing

You can test the patent scraping functionality by running the agents through the main API.

This will test both Google Patents and USPTO scraping.

## Notes

- Playwright requires ~150MB for Chromium browser
- Runs in headless mode (no GUI)
- Respects rate limits to avoid blocking
- Handles errors gracefully (returns empty results if scraping fails)




