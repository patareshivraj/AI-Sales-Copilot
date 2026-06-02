from schemas.icp_schema import ICPProfile
from schemas.prospect_schema import ProspectList
from core.llm import LLMService
from core.search_manager import SearchManager
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
        self.search = SearchManager()

    def find_prospects(self, icp: ICPProfile, limit: int = 15) -> ProspectList:
        # Build varied search queries — randomize region to ensure fresh results each run
        queries = []
        for kw in icp.keywords:
            if icp.regions:
                region = random.choice(icp.regions)
                queries.append(f'"{kw}" companies {icp.market_type} {region}')
            else:
                queries.append(f'"{kw}" companies {icp.market_type}')

        # Use SearchManager: Cache → Brave → DuckDuckGo fallback
        raw_results = self.search.search_batch(queries, max_results=10)

        # Log provider metrics
        metrics = self.search.get_metrics()
        print(f"[SearchManager Metrics] {metrics}")

        # Format results for the LLM prompt
        formatted_results = []
        for r in raw_results:
            formatted_results.append(
                f"Title: {r.get('title')}\nLink: {r.get('href', '')}\nSnippet: {r.get('body')}\n---"
            )

        if not formatted_results:
            print("[ProspectFinder] No search results returned from any provider.")
            return ProspectList(prospects=[])

        prompt = PROSPECT_PROMPT.format(
            industries=", ".join(icp.industries),
            market_type=icp.market_type,
            keywords=", ".join(icp.keywords),
            search_results="\n".join(formatted_results[:30]),
            limit=limit
        )

        try:
            response = self.llm.generate_structured(prompt, ProspectList)
            if isinstance(response, ProspectList):
                return response
            return ProspectList(prospects=[])
        except Exception as e:
            print(f"Agent error: {e}")
            return ProspectList(prospects=[])
