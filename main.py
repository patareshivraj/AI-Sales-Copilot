from core.llm import LLMService
from pydantic import BaseModel, Field
from typing import List

# Define the expected JSON schema for the Phase 1.8 test
class ICPProfile(BaseModel):
    industries: List[str] = Field(description="Target industries based on the offering")
    company_size: str = Field(description="Ideal company size or range")
    decision_makers: List[str] = Field(description="Job titles of key decision makers")

def run_tests():
    print("Initializing LLM Service...")
    # Initialize the LLM layer abstraction
    llm = LLMService()

    print("\n=============================================")
    print("Phase 1.7 — Test LLM (Unstructured)")
    print("=============================================")
    prompt_1 = "Who are some manufacturing companies in Pune?"
    print(f"Prompt: {prompt_1}\n")
    
    try:
        # Ask LLM a standard text question
        response_1 = llm.generate(prompt_1)
        print("Expected: Model responds successfully.")
        print(f"Result:\n{response_1}")
    except Exception as e:
        print(f"Test Failed: {e}")

    print("\n=============================================")
    print("Phase 1.8 — Structured Output Test (JSON)")
    print("=============================================")
    prompt_2 = "We sell AI transformation services. Generate ICP in JSON format."
    print(f"Prompt: {prompt_2}\n")
    
    try:
        # Ask LLM for a structured Pydantic object
        response_2 = llm.generate_structured(prompt_2, ICPProfile)
        
        print("Expected: JSON structure matching ICP schema.")
        print("Result:")
        # Convert the resulting Pydantic model to nicely formatted JSON
        print(response_2.model_dump_json(indent=2))
        
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    run_tests()
