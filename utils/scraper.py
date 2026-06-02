"""
Upgraded web scraper — Phase 12.3
==================================
Uses Trafilatura as primary extractor (cleaner text, removes boilerplate/ads).
Falls back to BeautifulSoup if Trafilatura fails or returns nothing.
"""

import requests
import trafilatura
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def scrape_website(url: str) -> str:
    """
    Fetches and cleans website text.
    Strategy:
      1. Trafilatura — best for article/blog/about pages (removes nav, ads, boilerplate)
      2. BeautifulSoup — fallback for JavaScript-heavy or structured pages
    Returns cleaned text string (max 6000 chars), or empty string on failure.
    """
    if not url:
        return ""

    if not url.startswith("http"):
        url = "https://" + url

    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        if response.status_code != 200:
            return ""

        raw_html = response.text

        # ── Strategy 1: Trafilatura ───────────────────────────────────────────
        text = trafilatura.extract(
            raw_html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )

        if text and len(text.strip()) >= 100:
            return text[:6000]

        # ── Strategy 2: BeautifulSoup fallback ───────────────────────────────
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.extract()
        bs_text = soup.get_text(separator=" ", strip=True)
        bs_text = re.sub(r"\s+", " ", bs_text)
        return bs_text[:6000]

    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        return ""
