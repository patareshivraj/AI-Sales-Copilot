from core.llm import LLMService
from schemas.icp_schema import ICPProfile

ICP_PROMPT_TEMPLATE = """You are an expert B2B GTM strategist.

Your task is to create an Ideal Customer Profile (ICP) from a business offering.

Analyze:
1. Industries most likely to buy
2. Ideal company size
3. Key decision makers
4. Geographic regions
5. Market type (e.g., 'India', 'Global', 'Local')
6. Search keywords (highly specific phrases for finding these prospects later)
7. Brief reasoning

Rules:
* Focus on realistic B2B buyers.
* Prioritize organizations with clear business value.
* Avoid generic answers.
* Think like a sales strategist.
* IMPORTANT: If the business offering is empty, gibberish, or just a greeting like "Hello", do NOT hallucinate an ICP. Instead, use the 'error' field to output "Insufficient business offering provided." and leave the rest blank.

Business Offering:
{user_input}
"""

class ICPBuilderAgent:
    def __init__(self):
        self.llm = LLMService()

    def build_icp(self, business_offering: str) -> ICPProfile:
        # Pre-flight check for obviously empty strings
        if not business_offering or not business_offering.strip():
            return ICPProfile(error="Insufficient business offering provided.")

        prompt = ICP_PROMPT_TEMPLATE.format(user_input=business_offering)
        
        try:
            response = self.llm.generate_structured(prompt, ICPProfile)
            
            # If for some reason the LLM failed to return the object, handle it gracefully
            if not isinstance(response, ICPProfile):
                return ICPProfile(error=f"Agent failed to return structured data. Raw: {response}")
                
            return response
        except Exception as e:
            return ICPProfile(error=f"Internal agent error: {str(e)}")
