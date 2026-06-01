import sys
from core.llm import LLMService
from pydantic import BaseModel
from typing import List

class ICPProfile(BaseModel):
    industries: List[str]
    company_size: str
    decision_makers: List[str]

def run_tests():
    print("Initializing LLM Service...")
    llm = LLMService()

    print("\n--- TEST 1: Basic LLM Connection ---")
    res1 = llm.generate("Say hello in one sentence.")
    print("Response:", res1)
    if res1 and not res1.startswith("API Error"):
        print("TEST 1 - Basic Generation\nPASS")
    else:
        print("TEST 1 - Basic Generation\nFAIL")

    print("\n--- TEST 2: Business Question ---")
    res2 = llm.generate("List 5 manufacturing companies in Pune.")
    print("Response:\n" + res2)
    if res2 and len(res2) > 20 and not res2.startswith("API Error"):
        print("TEST 2 - Business Question\nPASS")
    else:
        print("TEST 2 - Business Question\nFAIL")

    print("\n--- TEST 3: Structured Output ---")
    prompt_icp = "We provide AI Transformation Services.\n\nGenerate ICP."
    res3 = llm.generate_structured(prompt_icp, ICPProfile)
    print("Response:", res3)
    if isinstance(res3, ICPProfile):
        print("TEST 3 - Structured Output\nPASS")
    else:
        print("TEST 3 - Structured Output\nFAIL")

    print("\n--- TEST 4: JSON Reliability (5 runs) ---")
    success_count = 0
    for i in range(5):
        res4 = llm.generate_structured(prompt_icp, ICPProfile)
        if isinstance(res4, ICPProfile):
            print(f"Run {i+1} -> Success")
            success_count += 1
        else:
            print(f"Run {i+1} -> Fail: {res4}")
    
    if success_count == 5:
        print("TEST 4 - Reliability (5 runs)\nPASS")
    else:
        print("TEST 4 - Reliability (5 runs)\nFAIL")

    print("\n--- TEST 5: Empty Input ---")
    res5 = llm.generate_structured("", ICPProfile)
    print("Response:", res5)

    print("\n--- TEST 6: API Failure Handling ---")
    invalid_llm = LLMService(api_key="invalid_key")
    res6 = invalid_llm.generate("hello")
    print("Response:", res6)

if __name__ == "__main__":
    run_tests()
