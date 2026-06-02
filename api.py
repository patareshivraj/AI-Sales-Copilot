import uuid
import json
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uvicorn

from core.orchestrator import SalesCopilotWorkflow
import demo

app = FastAPI(
    title="AI Sales Copilot API",
    description="Enterprise Multi-Agent Lead Intelligence Engine",
    version="1.1.0"
)

# In-memory job store (in production, use Redis or Postgres)
jobs_db = {}

class CopilotRequest(BaseModel):
    query: str = "We provide AI Transformation Services. Find potential customers in India."

def run_pipeline_background(job_id: str, query: str):
    try:
        workflow = SalesCopilotWorkflow()
        final_report = workflow.run(query)
        
        if final_report:
            os.makedirs("outputs", exist_ok=True)
            # Save specific job report
            with open(f"outputs/job_{job_id}.json", "w") as f:
                json.dump(final_report, f, indent=4)
            
            # Also save as latest for legacy compatibility
            with open("outputs/final_report.json", "w") as f:
                json.dump(final_report, f, indent=4)
                
            demo.generate_demo_report()
            jobs_db[job_id]["status"] = "completed"
            jobs_db[job_id]["results_path"] = f"outputs/job_{job_id}.json"
        else:
            jobs_db[job_id]["status"] = "failed"
            jobs_db[job_id]["error"] = "Pipeline returned None"
    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(e)

@app.post("/api/v1/jobs", summary="Start Async Pipeline Job")
def start_job(request: CopilotRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "query": request.query
    }
    background_tasks.add_task(run_pipeline_background, job_id, request.query)
    return {"job_id": job_id, "status": "processing", "message": "Job started in the background."}

@app.get("/api/v1/jobs/{job_id}", summary="Check Job Status")
def get_job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"job_id": job_id, "status": jobs_db[job_id]["status"]}

@app.get("/api/v1/jobs/{job_id}/results", summary="Get Job Results")
def get_job_results(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = jobs_db[job_id]
    
    if job["status"] == "processing":
        return {"status": "processing", "message": "Job is still running."}
    
    if job["status"] == "failed":
        return {"status": "failed", "message": job.get("error", "Unknown error")}
        
    try:
        with open(job["results_path"], "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Result file not found")

@app.get("/api/v1/reports/latest", summary="Get Latest Report Metrics")
def get_latest_report():
    try:
        with open("reports/lead_report.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": "error", "message": "No reports generated yet."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
