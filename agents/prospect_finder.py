from ddgs import DDGS
from schemas.icp_schema import ICPProfile
from schemas.prospect_schema import ProspectList
from core.llm import LLMService

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
5. Ensure the 'source' is set to 'DuckDuckGo'.
6. Return up to {limit} companies. DO NOT invent or hallucinate companies.

Extract the prospects now.
"""

class ProspectFinderAgent:
    def __init__(self):
        self.llm = LLMService()

    def find_prospects(self, icp: ICPProfile, limit: int = 15) -> ProspectList:
        queries = []
        # Build search queries from keywords and market type
        # E.g., '"digital transformation" companies India'
        target_keywords = icp.keywords[:1] if icp.keywords else icp.industries[:1]
        market = icp.market_type if icp.market_type else "Global"
        
        for kw in target_keywords:
            query = f'"{kw}" companies {market}'
            queries.append(query)
            
        raw_results = []
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = ddgs.text(query, max_results=10)
                    if results:
                        raw_results.extend(results)
        except Exception as e:
            print(f"Search failed: {e}")
            
        # Deduplicate and format
        seen_links = set()
        formatted_results = []
        for r in raw_results:
            link = r.get("href", "")
            if link not in seen_links:
                seen_links.add(link)
                formatted_results.append(
                    f"Title: {r.get('title')}\nLink: {link}\nSnippet: {r.get('body')}\n---"
                )
                
        if not formatted_results:
            return ProspectList(prospects=[])
            
        prompt = PROSPECT_PROMPT.format(
            industries=", ".join(icp.industries),
            market_type=market,
            keywords=", ".join(icp.keywords),
            search_results="\n".join(formatted_results[:30]), # Limit context size
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
