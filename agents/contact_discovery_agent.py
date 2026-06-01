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
2. DO NOT invent or guess email addresses. If you do not see a literal email address (e.g. name@company.com), set email to null and verification_level to 'not_found'.
3. If you find a name and valid LinkedIn URL, set verification_level to 'verified'.
4. If no person is found, return nulls and 'not_found'.

Extract the contact now.
"""

class ContactDiscoveryAgent:
    def __init__(self):
        self.llm = LLMService(temperature=0.1)

    def find_contact(self, company: str, icp: ICPProfile) -> Contact:
        queries = []
        for dm in icp.decision_makers[:2]:
            # Focus search entirely on finding a LinkedIn profile for the specific role at the specific company
            queries.append(f'"{dm}" "{company}" site:linkedin.com/in/')
            
        raw_results = []
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = ddgs.text(query, max_results=3)
                    if results:
                        raw_results.extend(results)
        except Exception as e:
            print(f"Contact search failed: {e}")
            
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
                verification_level="not_found"
            )
            
        prompt = CONTACT_PROMPT.format(
            company=company,
            decision_makers=", ".join(icp.decision_makers),
            search_results="\n".join(formatted_results)
        )
        
        try:
            response = self.llm.generate_structured(prompt, Contact)
            if isinstance(response, Contact):
                # Ensure company name persists
                response.company = company
                return response
        except Exception:
            pass
            
        return Contact(
            company=company,
            verification_level="not_found"
        )
