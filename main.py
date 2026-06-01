import json
from core.orchestrator import SalesCopilotWorkflow

def main():
    print("Initializing Sales Copilot Workflow...")
    workflow = SalesCopilotWorkflow()
    
    query = "We provide AI Transformation Services. Find potential customers in India."
    print(f"\nUser Query: {query}")
    
    final_report = workflow.run(query)
    
    if final_report:
        with open("outputs/final_report.json", "w") as f:
            json.dump(final_report, f, indent=4)
        print("\nReport successfully saved to outputs/final_report.json")

if __name__ == "__main__":
    main()
