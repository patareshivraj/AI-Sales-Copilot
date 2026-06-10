import os
import requests
from ddgs import DDGS
from schemas.icp_schema import ICPProfile
from schemas.contact_schema import Contact
from core.llm import LLMService

CONTACT_PROMPT = """You are an expert Data Researcher.

I am providing you with public search results for a decision maker at the target company.
Your goal is to extract the Contact details safely and accurately.

Company: {company}
Target Decision Makers: {decision_makers}

Search Results:
{search_results}

Rules:
1. Extract the name, title, and linkedin_url ONLY if they explicitly appear in the search results.
2. DO NOT invent or guess email addresses. If you do not see a literal email address, set email to null and verification_level to 'not_found'.
3. Set 'source_url' to the exact link where you found the best match. Set 'source_type' to 'linkedin_search' if the source is LinkedIn.
4. Set 'contact_confidence' (0-100) based on how well the title matches the Target Decision Makers and the company name.
5. If no person is found, return nulls, 'not_found', 'none' for source, and 0 for confidence.

Extract the contact now.
"""

class ContactDiscoveryAgent:
    def __init__(self):
        self.llm = LLMService(temperature=0.1)

    def find_contact(self, company: str, icp: ICPProfile) -> Contact:
        """
        Discover contacts using Apollo People Search, falling back to DDG search on any failure.
        """
        api_key = os.getenv("APOLLO_API_KEY", "").strip()
        
        # Determine target titles in order of priority
        target_titles = []
        if hasattr(icp, "decision_makers") and icp.decision_makers:
            target_titles = [t.strip() for t in icp.decision_makers if t.strip()]
        if not target_titles:
            target_titles = ["CTO", "Chief Digital Officer", "VP Engineering", "Head of AI", "Director of Technology"]

        apollo_success = False
        people = []

        # ── 1. Apollo People Search ───────────────────────────────────────────
        if api_key:
            endpoint = "https://api.apollo.io/api/v1/mixed_people/api_search"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            }
            payload = {
                "q_organization_name": company,
                "person_titles": target_titles,
                "per_page": 20
            }
            try:
                # 10s timeout
                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    people = data.get("people", [])
                    apollo_success = True
                elif response.status_code == 429:
                    print("[ContactDiscoveryAgent] ERROR 429: Apollo Rate limit reached. Fallback to DDG.")
                else:
                    print(f"[ContactDiscoveryAgent] ERROR {response.status_code} from Apollo. Fallback to DDG.")
            except Exception as e:
                print(f"[ContactDiscoveryAgent] Apollo search exception: {e}. Fallback to DDG.")

        # ── 2. Process Apollo Results ──────────────────────────────────────────
        if apollo_success and people:
            # Find the best match according to title priority list
            best_person = None
            for title_to_match in target_titles:
                for p in people:
                    if p.get("title", "").lower().strip() == title_to_match.lower().strip():
                        best_person = p
                        break
                if best_person:
                    break
            
            # Fallback to the first found person if no exact title match
            if not best_person:
                best_person = people[0]

            first_name = best_person.get("first_name", "")
            last_name = best_person.get("last_name") or best_person.get("last_name_obfuscated") or ""
            full_name = f"{first_name} {last_name}".strip()

            return Contact(
                company=company,
                contact_name=full_name if full_name else None,
                title=best_person.get("title"),
                linkedin_url=best_person.get("linkedin_url"),
                email=None, # Never invent emails
                verification_level="apollo_verified",
                source_url=best_person.get("linkedin_url") or "https://apollo.io",
                source_type="apollo",
                contact_confidence=95,
                apollo_id=best_person.get("id")
            )

        # ── 3. Fallback: DuckDuckGo / LinkedIn Scraping ───────────────────────
        print(f"[ContactDiscoveryAgent] Falling back to DDG search for {company}...")
        queries = []
        for dm in target_titles[:2]:
            queries.append(f'"{dm}" "{company}" site:linkedin.com/in/')
            
        raw_results = []
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = ddgs.text(query, max_results=3)
                    if results:
                        raw_results.extend(results)
        except Exception as e:
            print(f"[ContactDiscoveryAgent] DDG search fallback failed: {e}")
            
        formatted_results = []
        seen_links = set()
        for r in raw_results:
            link = r.get("href", "")
            if link not in seen_links:
                seen_links.add(link)
                formatted_results.append(f"Title: {r.get('title')}\nLink: {link}\nSnippet: {r.get('body')}\n---")
            
        if not formatted_results:
            return Contact(
                company=company,
                contact_name=None,
                title=None,
                linkedin_url=None,
                email=None,
                verification_level="not_found",
                source_type="none",
                contact_confidence=0
            )
            
        prompt = CONTACT_PROMPT.format(
            company=company,
            decision_makers=", ".join(target_titles),
            search_results="\n".join(formatted_results)
        )
        
        try:
            response = self.llm.generate_structured(prompt, Contact)
            if isinstance(response, Contact):
                response.company = company
                return response
        except Exception as e:
            print(f"[ContactDiscoveryAgent] LLM fallback parsing error: {e}")
            
        return Contact(
            company=company,
            verification_level="not_found",
            source_type="none",
            contact_confidence=0
        )
