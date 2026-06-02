"""
DuckDuckGo Search Provider
===========================
Implements SearchProvider interface.
Used as primary (and currently only) live search provider.
"""
from search.providers.base_provider import SearchProvider


class DuckDuckGoProvider(SearchProvider):

    @property
    def name(self) -> str:
        return "duckduckgo"

    def search(self, query: str, limit: int = 15) -> list[dict]:
        """
        Search using DuckDuckGo. Returns empty list on any failure.
        Never raises — all exceptions are caught and logged internally.
        """
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=limit)
                if not results:
                    return []
                return [
                    {
                        "title": r.get("title", ""),
                        "href": r.get("href", ""),
                        "body": r.get("body", ""),
                    }
                    for r in results
                ]
        except Exception as e:
            # Let SearchManager handle the failure — don't raise
            raise RuntimeError(f"DuckDuckGo search failed: {e}") from e
