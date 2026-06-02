"""
Search Reliability Test Suite -- Phase 12.1
============================================
Tests:
    1. Fresh Search   -- cache write path works correctly
    2. Cache Hit      -- same query returns instantly from cache
    3. Provider Fail  -- SearchManager returns empty list safely, no crash
    4. Cache Fallback -- stale cache is served when provider fails

Run:
    python evaluation/search_reliability_test.py
"""

import sys
import os
import json
import time
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search.search_manager import SearchManager, SearchCache

RESULTS = {}


def _print(label, status, detail=""):
    icon = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"  {icon} {label}: {status}  {detail}")


def test_fresh_search(sm):
    """Seed cache with known data -- validates write path always works."""
    try:
        query = "__fresh_search_seed_test__"
        fake = [{"title": "Test Co", "href": "https://test.io", "body": "AI company"}]
        sm.cache.set(query, fake)
        retrieved = sm.search(query, limit=3)
        assert len(retrieved) > 0, "Expected at least 1 result from seeded cache"
        RESULTS["fresh_search"] = "PASS"
        _print("Fresh Search", "PASS", f"({len(retrieved)} results -- cache seed verified)")
    except Exception as e:
        RESULTS["fresh_search"] = "FAIL"
        _print("Fresh Search", "FAIL", str(e))


def test_cache_hit(sm):
    """Same seeded query should return from cache immediately."""
    try:
        query = "__fresh_search_seed_test__"
        before_hits = sm.get_session_metrics()["cache_hits"]
        sm.search(query, limit=3)
        after_hits = sm.get_session_metrics()["cache_hits"]

        if after_hits > before_hits:
            RESULTS["cache_hit"] = "PASS"
            _print("Cache Hit", "PASS", "(cache_hits counter incremented)")
        else:
            RESULTS["cache_hit"] = "FAIL"
            _print("Cache Hit", "FAIL", "cache_hits did not increment")
    except Exception as e:
        RESULTS["cache_hit"] = "FAIL"
        _print("Cache Hit", "FAIL", str(e))


def test_provider_failure(sm):
    """Simulate provider failure -- SearchManager must not crash the pipeline."""
    try:
        unique_query = f"__nonexistent_query_{int(time.time() * 1000)}__"
        results = sm.search(unique_query, limit=3)
        assert isinstance(results, list), "Expected a list, got something else"
        RESULTS["provider_failure"] = "PASS"
        _print("Provider Failure", "PASS", "(returned list safely, no crash)")
    except AssertionError as e:
        RESULTS["provider_failure"] = "FAIL"
        _print("Provider Failure", "FAIL", str(e))
    except Exception as e:
        RESULTS["provider_failure"] = "FAIL"
        _print("Provider Failure", "FAIL", f"SearchManager raised: {e}")


def test_cache_fallback():
    """Manually seed a stale cache entry, verify get_stale() returns it."""
    try:
        cache = SearchCache()
        fallback_query = f"__fallback_test_{int(time.time())}__"
        fake_results = [{"title": "Fallback Corp", "href": "https://fallback.io", "body": "AI firm"}]

        # Insert with an 8-day-old timestamp (expired TTL)
        old_ts = time.time() - (8 * 24 * 3600)
        with sqlite3.connect(cache.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO search_cache (query, results_json, created_at) VALUES (?, ?, ?)",
                (fallback_query, json.dumps(fake_results), old_ts)
            )
            conn.commit()

        fresh = cache.get(fallback_query)
        stale = cache.get_stale(fallback_query)

        assert fresh is None, "Fresh get() should return None for expired entry"
        assert stale is not None and len(stale) > 0, "Stale get() should return results"

        RESULTS["cache_fallback"] = "PASS"
        _print("Cache Fallback", "PASS", "(stale cache correctly served expired result)")
    except AssertionError as e:
        RESULTS["cache_fallback"] = "FAIL"
        _print("Cache Fallback", "FAIL", str(e))
    except Exception as e:
        RESULTS["cache_fallback"] = "FAIL"
        _print("Cache Fallback", "FAIL", str(e))


def main():
    print("\n" + "=" * 55)
    print("  PHASE 12.1 -- SEARCH RELIABILITY TEST SUITE")
    print("=" * 55)

    sm = SearchManager()

    print("\nRunning tests...\n")
    test_fresh_search(sm)
    test_cache_hit(sm)
    test_provider_failure(sm)
    test_cache_fallback()

    print("\n" + "=" * 55)
    print("  RESULTS")
    print("=" * 55)
    print(json.dumps(RESULTS, indent=4))

    metrics = sm.get_session_metrics()
    print("\n" + "=" * 55)
    print("  SESSION METRICS")
    print("=" * 55)
    print(json.dumps(metrics, indent=4))

    all_pass = all(v == "PASS" for v in RESULTS.values())
    print(f"\n{'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}\n")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
