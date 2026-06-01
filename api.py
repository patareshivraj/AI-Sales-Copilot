from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json
import os

from core.orchestrator import SalesCopilotWorkflow
import demo

app = FastAPI(
    title="AI Sales Copilot API",
    description="Enterprise Multi-Agent Lead Intelligence Engine",
    version="1.0.0"
)

class CopilotRequest(BaseModel):
    query: str = "We provide AI Transformation Services. Find potential customers in India."

@app.post("/api/v1/run", summary="Run Full Sales Copilot Pipeline")
def run_pipeline(request: CopilotRequest):
    workflow = SalesCopilotWorkflow()
    final_report = workflow.run(request.query)
    
    if final_report:
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/final_report.json", "w") as f:
            json.dump(final_report, f, indent=4)
        
        # Update artifacts
        demo.generate_demo_report()
        return {"status": "success", "report": final_report}
    return {"status": "failed", "message": "Pipeline returned None"}

@app.get("/api/v1/reports/latest", summary="Get Latest Report Metrics")
def get_latest_report():
    try:
        with open("reports/lead_report.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": "error", "message": "No reports generated yet."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
