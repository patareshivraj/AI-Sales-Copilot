"""
SearchManager — Phase 12.1 Reliability Layer
=============================================
Architecture:
    Query → SQLite Cache → Brave Search → DuckDuckGo Fallback

- Cache TTL: 7 days (avoids re-searching same keywords)
- Brave Search: Official API, free tier (2000 queries/month)
- DuckDuckGo: Fallback only (rate-limited, unstable)
- Metrics: Logs provider success/failure on every call
"""

import sqlite3
import json
import time
import os
import requests
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
CACHE_DB_PATH = "outputs/search_cache.db"
CACHE_TTL_DAYS = 7
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")  # Optional - set in .env

# ── Metrics tracker (in-memory per session) ───────────────────────────────────
_metrics = {
    "cache_hits": 0,
    "brave_success": 0,
    "brave_failure": 0,
    "ddg_success": 0,
    "ddg_failure": 0,
}


class SearchCache:
    """SQLite-backed search result cache with 7-day TTL."""

    def __init__(self):
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(CACHE_DB_PATH, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                query TEXT PRIMARY KEY,
                results TEXT NOT NULL,
                cached_at REAL NOT NULL
            )
        """)
        self.conn.commit()

    def get(self, query: str) -> list | None:
        cutoff = time.time() - (CACHE_TTL_DAYS * 86400)
        row = self.conn.execute(
            "SELECT results, cached_at FROM search_cache WHERE query = ?",
            (query,)
        ).fetchone()
        if row and row[1] >= cutoff:
            return json.loads(row[0])
        return None

    def set(self, query: str, results: list):
        self.conn.execute(
            "INSERT OR REPLACE INTO search_cache (query, results, cached_at) VALUES (?, ?, ?)",
            (query, json.dumps(results), time.time())
        )
        self.conn.commit()

    def clear_expired(self):
        cutoff = time.time() - (CACHE_TTL_DAYS * 86400)
        self.conn.execute("DELETE FROM search_cache WHERE cached_at < ?", (cutoff,))
        self.conn.commit()


class BraveSearchProvider:
    """
    Official Brave Search API provider.
    Free tier: 2000 queries/month. Sign up at https://brave.com/search/api/
    Set BRAVE_API_KEY in your .env file.
    """
    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def search(self, query: str, max_results: int = 10) -> list:
        if not BRAVE_API_KEY:
            raise ValueError("BRAVE_API_KEY not set in .env")

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": BRAVE_API_KEY,
        }
        params = {"q": query, "count": min(max_results, 20), "safesearch": "off"}

        resp = requests.get(self.BASE_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "href": item.get("url", ""),
                "body": item.get("description", ""),
            })
        return results


class DuckDuckGoProvider:
    """DuckDuckGo fallback provider (unauthenticated, rate-limited)."""

    def search(self, query: str, max_results: int = 10) -> list:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            return results if results else []


class SearchManager:
    """
    Unified search abstraction with cache + provider fallback chain.

    Usage:
        sm = SearchManager()
        results = sm.search("AI companies in India")
        print(sm.get_metrics())
    """

    def __init__(self):
        self.cache = SearchCache()
        self.brave = BraveSearchProvider()
        self.ddg = DuckDuckGoProvider()

    def search(self, query: str, max_results: int = 10) -> list:
        # 1. Try cache first
        cached = self.cache.get(query)
        if cached:
            _metrics["cache_hits"] += 1
            print(f"[SearchManager] CACHE HIT: '{query[:60]}...' ({len(cached)} results)")
            return cached

        # 2. Try Brave Search (primary)
        if BRAVE_API_KEY:
            try:
                results = self.brave.search(query, max_results)
                if results:
                    _metrics["brave_success"] += 1
                    self.cache.set(query, results)
                    print(f"[SearchManager] BRAVE SUCCESS: '{query[:60]}...' ({len(results)} results)")
                    return results
            except Exception as e:
                _metrics["brave_failure"] += 1
                print(f"[SearchManager] BRAVE FAILED: {e}")

        # 3. Fall back to DuckDuckGo
        try:
            results = self.ddg.search(query, max_results)
            if results:
                _metrics["ddg_success"] += 1
                self.cache.set(query, results)
                print(f"[SearchManager] DDG SUCCESS: '{query[:60]}...' ({len(results)} results)")
                return results
        except Exception as e:
            _metrics["ddg_failure"] += 1
            print(f"[SearchManager] DDG FAILED: {e}")

        # 4. All providers failed — return empty
        print(f"[SearchManager] ALL PROVIDERS FAILED for: '{query[:60]}...'")
        return []

    def search_batch(self, queries: list[str], max_results: int = 10) -> list:
        """Run multiple queries and merge deduplicated results."""
        seen_links = set()
        all_results = []
        for q in queries:
            for r in self.search(q, max_results):
                link = r.get("href", "")
                if link and link not in seen_links:
                    seen_links.add(link)
                    all_results.append(r)
        return all_results

    def get_metrics(self) -> dict:
        return dict(_metrics)
