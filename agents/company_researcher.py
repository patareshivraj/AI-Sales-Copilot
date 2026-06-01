from core.llm import LLMService
from schemas.research_schema import CompanyResearch
from utils.scraper import scrape_website

RESEARCH_PROMPT = """You are an expert Business Research Agent.

Your task is to analyze the text scraped from a company's website and extract structured information.

Company: {company}
Website: {website}

Scraped Website Content:
{scraped_text}

Rules:
1. ONLY use the provided scraped content. DO NOT invent or hallucinate information.
2. If the data isn't found in the text, return null or empty lists for those fields. Do not guess.
3. Determine 'ai_readiness' (High/Medium/Low) based on whether they mention AI, ML, digital transformation, data engineering, etc.
4. Provide a 'research_confidence' score (0-100) based on how much clear information was available.
5. Set 'status' to "Success" if data was found, or "Insufficient information" if the scraped text is useless.

Extract the research profile now.
"""

class CompanyResearcherAgent:
    def __init__(self):
        self.llm = LLMService()

    def research_company(self, company_name: str, website: str) -> CompanyResearch:
        scraped_text = scrape_website(website)
        
        if not scraped_text or len(scraped_text) < 50:
            return CompanyResearch(
                company=company_name,
                website=website,
                industry=None,
                summary=None,
                research_confidence=0,
                status="Insufficient information"
            )
            
        prompt = RESEARCH_PROMPT.format(
            company=company_name,
            website=website,
            scraped_text=scraped_text
        )
        
        try:
            response = self.llm.generate_structured(prompt, CompanyResearch)
            if isinstance(response, CompanyResearch):
                return response
        except Exception as e:
            return CompanyResearch(
                company=company_name,
                website=website,
                research_confidence=0,
                status=f"Agent error: {str(e)}"
            )
            
        return CompanyResearch(
            company=company_name,
            website=website,
            research_confidence=0,
            status="Failed to extract structured output."
        )
