import sys
import os

# Add the parent directory to the python path so we can import from core, agents, schemas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.icp_builder import ICPBuilderAgent

def run_tests():
    agent = ICPBuilderAgent()
    
    test_cases = [
        ("TEST 1", "We provide AI Transformation Services."),
        ("TEST 2", "We provide Cloud Migration Services."),
        ("TEST 3", "We provide Cybersecurity Consulting."),
        ("TEST 4", "We provide Data Engineering Solutions."),
        ("TEST 5", "We provide HR Automation Software."),
        ("EDGE 1", ""),
        ("EDGE 2", "Hello")
    ]
    
    print("====================================")
    print("ICP BUILDER AGENT - VALIDATION TESTS")
    print("====================================\n")
    
    for name, input_text in test_cases:
        print(f"--- {name} ---")
        print(f"Input: \"{input_text}\"")
        
        result = agent.build_icp(input_text)
        
        print("Result:")
        print(result.model_dump_json(indent=2))
        print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    run_tests()
