"""
SearchManager — Phase 12.1 Reliability Layer
=============================================
Architecture:
    Query
      ↓
    SQLite Cache (7-day TTL)  ← Cache hit? Return immediately.
      ↓ Miss
    Provider Chain (DuckDuckGo → future: Brave, Google)
      ↓ All fail
    Cached fallback (any age)
      ↓ No cache at all
    Return {"status": "search_failed", "reason": "provider_unavailable"}

Observability:
    All events logged to logs/search.log
"""

import sqlite3
import json
import time
import os
import logging
from datetime import datetime
from search.providers.duckduckgo_provider import DuckDuckGoProvider

# ── Paths ─────────────────────────────────────────────────────────────────────
DB_PATH   = "database/search_cache.db"
LOG_PATH  = "logs/search.log"
CACHE_TTL = 7 * 24 * 3600  # 7 days in seconds

# ── Logger setup ──────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
os.makedirs("database", exist_ok=True)

_logger = logging.getLogger("SearchManager")
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
    fh.setFormatter(logging.Formatter(
        "[%(asctime)s] [SEARCH] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    _logger.addHandler(fh)
    # Also print to console so terminal shows search events
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[SearchManager] %(message)s"))
    _logger.addHandler(ch)

# ── Session metrics (reset on each server restart) ────────────────────────────
_session_metrics = {
    "cache_hits":    0,
    "cache_misses":  0,
    "provider_success": 0,
    "provider_failure": 0,
    "cache_fallback":   0,
}


# ══════════════════════════════════════════════════════════════════════════════
# SQLite Cache
# ══════════════════════════════════════════════════════════════════════════════

class SearchCache:
    """
    SQLite-backed search result cache.

    Schema:
        search_cache(query TEXT PRIMARY KEY, results_json TEXT, created_at REAL)
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    query       TEXT PRIMARY KEY,
                    results_json TEXT NOT NULL,
                    created_at  REAL NOT NULL
                )
            """)
            conn.commit()

    def get(self, query: str, max_age: int = CACHE_TTL) -> list | None:
        """Return cached results if fresh enough, else None."""
        cutoff = time.time() - max_age
        with self._connect() as conn:
            row = conn.execute(
                "SELECT results_json, created_at FROM search_cache WHERE query = ?",
                (query,)
            ).fetchone()
        if row and row[1] >= cutoff:
            return json.loads(row[0])
        return None

    def get_stale(self, query: str) -> list | None:
        """Return any cached result regardless of age (for emergency fallback)."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT results_json FROM search_cache WHERE query = ?",
                (query,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def set(self, query: str, results: list):
        """Store results. Overwrites any existing entry for this query."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO search_cache (query, results_json, created_at) VALUES (?, ?, ?)",
                (query, json.dumps(results), time.time())
            )
            conn.commit()

    def stats(self) -> dict:
        """Return cache statistics."""
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM search_cache").fetchone()[0]
            fresh = conn.execute(
                "SELECT COUNT(*) FROM search_cache WHERE created_at >= ?",
                (time.time() - CACHE_TTL,)
            ).fetchone()[0]
        return {"total_entries": total, "fresh_entries": fresh, "stale_entries": total - fresh}


# ══════════════════════════════════════════════════════════════════════════════
# SearchManager
# ══════════════════════════════════════════════════════════════════════════════

class SearchManager:
    """
    Centralized search orchestration with cache-first architecture.

    Provider chain (in order):
        1. DuckDuckGoProvider  (active)
        2. BraveProvider       (stub — activate by setting BRAVE_API_KEY in .env)

    Usage:
        sm = SearchManager()
        results = sm.search("AI consulting firms India", limit=15)
        batch   = sm.search_batch(["query1", "query2"], limit=10)
        metrics = sm.get_session_metrics()
    """

    def __init__(self):
        self.cache = SearchCache()
        # Provider chain — add BraveProvider() here once API key is set
        self.providers = [
            DuckDuckGoProvider(),
        ]

    def search(self, query: str, limit: int = 15) -> list[dict]:
        """
        Execute a single query through: Cache → Providers → Stale Cache → Fail safe.
        Always returns a list (never raises).
        """
        t_start = time.time()

        # ── 1. Cache check (fresh) ────────────────────────────────────────────
        cached = self.cache.get(query)
        if cached:
            _session_metrics["cache_hits"] += 1
            duration = round(time.time() - t_start, 3)
            _logger.info(
                f"provider=cache | cache_hit=True | status=success | "
                f"results={len(cached)} | duration={duration}s | query=\"{query[:80]}\""
            )
            return cached

        _session_metrics["cache_misses"] += 1

        # ── 2. Live provider chain ────────────────────────────────────────────
        for provider in self.providers:
            try:
                results = provider.search(query, limit)
                if results:
                    self.cache.set(query, results)
                    _session_metrics["provider_success"] += 1
                    duration = round(time.time() - t_start, 3)
                    _logger.info(
                        f"provider={provider.name} | cache_hit=False | status=success | "
                        f"results={len(results)} | duration={duration}s | query=\"{query[:80]}\""
                    )
                    return results
            except Exception as e:
                _session_metrics["provider_failure"] += 1
                duration = round(time.time() - t_start, 3)
                _logger.warning(
                    f"provider={provider.name} | cache_hit=False | status=failure | "
                    f"error=\"{e}\" | duration={duration}s | query=\"{query[:80]}\""
                )

        # ── 3. Stale cache fallback ───────────────────────────────────────────
        stale = self.cache.get_stale(query)
        if stale:
            _session_metrics["cache_fallback"] += 1
            duration = round(time.time() - t_start, 3)
            _logger.warning(
                f"provider=stale_cache | cache_hit=True(stale) | status=recovered | "
                f"results={len(stale)} | duration={duration}s | query=\"{query[:80]}\""
            )
            return stale

        # ── 4. Complete failure — safe return ────────────────────────────────
        duration = round(time.time() - t_start, 3)
        _logger.error(
            f"provider=none | cache_hit=False | status=failed | "
            f"results=0 | duration={duration}s | query=\"{query[:80]}\""
        )
        return []

    def search_prospects(self, icp: any, limit: int = 15) -> list[dict]:
        """
        Execute search prospects:
        Apollo Company Search -> DuckDuckGo Fallback -> Cache -> []
        """
        from search.apollo_icp_adapter import translate_icp_to_apollo_payload
        from search.providers.apollo_company_provider import ApolloCompanyProvider
        
        t_start = time.time()
        
        # 1. Translate ICP
        try:
            payload = translate_icp_to_apollo_payload(icp)
        except Exception as e:
            _logger.error(f"Failed to translate ICP: {e}")
            payload = {}
            
        payload_key = "apollo_payload:" + json.dumps(payload, sort_keys=True)
        
        # Check cache (fresh) for Apollo payload
        cached = self.cache.get(payload_key)
        if cached:
            _session_metrics["cache_hits"] += 1
            duration = round(time.time() - t_start, 3)
            _logger.info(
                f"provider=cache_apollo | cache_hit=True | status=success | "
                f"results={len(cached)} | duration={duration}s"
            )
            return cached
            
        _session_metrics["cache_misses"] += 1
        
        # Try live Apollo structured search
        apollo_provider = ApolloCompanyProvider()
        try:
            results = apollo_provider.search_structured(payload, limit)
            if results:
                self.cache.set(payload_key, results)
                _session_metrics["provider_success"] += 1
                duration = round(time.time() - t_start, 3)
                _logger.info(
                    f"provider=apollo_company | cache_hit=False | status=success | "
                    f"results={len(results)} | duration={duration}s"
                )
                return results
        except Exception as e:
            _session_metrics["provider_failure"] += 1
            _logger.warning(f"Apollo company search failed: {e}")
            
        # Try stale cache fallback for Apollo payload
        stale_apollo = self.cache.get_stale(payload_key)
        if stale_apollo:
            _session_metrics["cache_fallback"] += 1
            duration = round(time.time() - t_start, 3)
            _logger.info(
                f"provider=stale_cache_apollo | cache_hit=True(stale) | status=recovered | "
                f"results={len(stale_apollo)} | duration={duration}s"
            )
            return stale_apollo

        # 2. DuckDuckGo Fallback
        _logger.warning("Apollo search failed or empty. Falling back to DuckDuckGo.")
        
        # Retrieve keywords, regions, market_type
        keywords = []
        regions = []
        market_type = ""
        
        if hasattr(icp, "model_dump"):
            icp_dict = icp.model_dump()
        elif hasattr(icp, "dict"):
            icp_dict = icp.dict()
        elif isinstance(icp, dict):
            icp_dict = icp
        else:
            icp_dict = {}
            
        keywords = icp_dict.get("keywords") or []
        regions = icp_dict.get("regions") or []
        market_type = icp_dict.get("market") or icp_dict.get("market_type") or ""
        
        queries = []
        for kw in keywords:
            if regions:
                import random
                region = random.choice(regions)
                queries.append(f'"{kw}" companies {market_type} {region}')
            else:
                queries.append(f'"{kw}" companies {market_type}')
                
        # search_batch uses fresh cache, live DDG, stale cache, or empty list
        ddg_results = self.search_batch(queries, limit)
        if ddg_results:
            return ddg_results
            
        return []

    def search_batch(self, queries: list[str], limit: int = 10) -> list[dict]:
        """
        Run multiple queries and merge deduplicated results.
        Used by ProspectFinderAgent for multi-keyword ICP searches.
        """
        seen_hrefs = set()
        all_results = []
        for q in queries:
            for r in self.search(q, limit):
                href = r.get("href", "")
                if href and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    all_results.append(r)
        return all_results

    def get_session_metrics(self) -> dict:
        """Return search performance metrics for the current session."""
        total = _session_metrics["cache_hits"] + _session_metrics["cache_misses"]
        hit_rate = round(
            (_session_metrics["cache_hits"] / total * 100) if total > 0 else 0, 1
        )
        return {
            **_session_metrics,
            "total_queries": total,
            "cache_hit_rate_percent": hit_rate,
            "cache_db_stats": self.cache.stats(),
        }
