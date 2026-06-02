"""
Base SearchProvider interface.
All future providers must implement this contract.
"""
from abc import ABC, abstractmethod


class SearchProvider(ABC):
    """Abstract base class for all search providers."""

    @abstractmethod
    def search(self, query: str, limit: int = 15) -> list[dict]:
        """
        Execute a search query.

        Args:
            query: The search string.
            limit: Maximum number of results to return.

        Returns:
            List of dicts with keys: title, href, body
            Returns empty list on failure — never raises.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier used in logs and metrics."""
        pass
