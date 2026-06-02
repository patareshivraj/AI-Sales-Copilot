from schemas.icp_schema import ICPProfile
from schemas.prospect_schema import ProspectList
from core.llm import LLMService
from search.search_manager import SearchManager
import random

PROSPECT_PROMPT = """You are an expert Sales Prospecting Agent.

I am providing you with an Ideal Customer Profile (ICP) and raw search results from the web.
Your job is to identify valid companies from the search results that match the ICP, and return a structured list of prospects.

ICP Details:
Industries: {industries}
Market Type: {market_type}
Keywords: {keywords}

Search Results:
{search_results}

Rules:
1. ONLY extract real companies that appear to match the ICP based on the snippets.
2. Exclude software review sites, generic directories, or news aggregators unless they are the actual prospect.
3. Calculate 'confidence' (0-100) deterministically: Industry Match (+40) + Keyword Match (+30) + Market/Location Match (+20) + Website Found (+10).
4. Populate 'matched_keywords' with the exact keywords found in the snippet.
5. Ensure the 'source' is set to 'SearchManager'.
6. Return a maximum of {limit} prospects, prioritized by highest confidence.
7. If no valid company prospects are found at all, return an empty list.

Return ONLY a JSON object matching the ProspectList schema.
"""


class ProspectFinderAgent:
    def __init__(self):
        self.llm = LLMService()
        self.search_manager = SearchManager()

    def find_prospects(self, icp: ICPProfile, limit: int = 15) -> ProspectList:
        # Build varied search queries — randomize region for fresh results each run
        queries = []
        for kw in icp.keywords:
            if icp.regions:
                region = random.choice(icp.regions)
                queries.append(f'"{kw}" companies {icp.market_type} {region}')
            else:
                queries.append(f'"{kw}" companies {icp.market_type}')

        # Delegate entirely to SearchManager: Cache → Provider → Stale Cache → []
        raw_results = self.search_manager.search_batch(queries, limit=10)

        # Log session metrics after each batch
        metrics = self.search_manager.get_session_metrics()
        print(f"\n[SearchManager Metrics] cache_hits={metrics['cache_hits']} | "
              f"provider_success={metrics['provider_success']} | "
              f"provider_failures={metrics['provider_failure']} | "
              f"cache_fallbacks={metrics['cache_fallback']} | "
              f"hit_rate={metrics['cache_hit_rate_percent']}%")

        if not raw_results:
            print("[ProspectFinder] No results from any source. Pipeline continues safely.")
            return ProspectList(prospects=[])

        # Format for LLM prompt
        formatted = [
            f"Title: {r.get('title')}\nLink: {r.get('href', '')}\nSnippet: {r.get('body')}\n---"
            for r in raw_results
        ]

        prompt = PROSPECT_PROMPT.format(
            industries=", ".join(icp.industries),
            market_type=icp.market_type,
            keywords=", ".join(icp.keywords),
            search_results="\n".join(formatted[:30]),
            limit=limit
        )

        try:
            response = self.llm.generate_structured(prompt, ProspectList)
            if isinstance(response, ProspectList):
                return response
            return ProspectList(prospects=[])
        except Exception as e:
            print(f"[ProspectFinder] Agent error: {e}")
            return ProspectList(prospects=[])
