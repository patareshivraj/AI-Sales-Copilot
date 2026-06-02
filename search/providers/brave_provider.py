"""
Brave Search Provider (STUB — Not yet implemented)
====================================================
Ready for activation once BRAVE_API_KEY is configured.
Implements the SearchProvider interface so SearchManager
can add it to the provider chain with zero code changes.
"""
from search.providers.base_provider import SearchProvider


class BraveProvider(SearchProvider):
    """
    Stub implementation for Brave Search API.

    To activate:
    1. Sign up at https://brave.com/search/api/ (2000 free queries/month)
    2. Set BRAVE_API_KEY=your_key in .env
    3. Uncomment this provider in search/search_manager.py

    Once active, this becomes the PRIMARY provider (more stable than DuckDuckGo).
    """

    @property
    def name(self) -> str:
        return "brave"

    def search(self, query: str, limit: int = 15) -> list[dict]:
        raise NotImplementedError(
            "BraveProvider is not yet active. "
            "Set BRAVE_API_KEY in .env and implement this method."
        )
