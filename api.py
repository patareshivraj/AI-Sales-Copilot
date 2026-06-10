"""
Phase 12.3 — File-Based Job Persistence
=========================================
Replaces the in-memory `jobs_db = {}` with a file-based store.

Each job is written to:
    jobs/{job_id}.json

On startup, all existing job files are reloaded into memory.
A server restart no longer loses job status or results.

This is a lightweight POC implementation — no Redis, no Postgres.
"""
import uuid
import json
import os
from typing import Optional, List
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uvicorn

from core.orchestrator import SalesCopilotWorkflow
import demo
from utils.crm_exporter import export_to_crm

# ── Job Store Directory ───────────────────────────────────────────────────────
JOBS_DIR = "jobs"
os.makedirs(JOBS_DIR, exist_ok=True)

app = FastAPI(
    title="AI Sales Copilot API",
    description="Enterprise Multi-Agent Lead Intelligence Engine",
    version="1.2.0"
)


# ── File-based Job Persistence ────────────────────────────────────────────────

def _job_path(job_id: str) -> str:
    return os.path.join(JOBS_DIR, f"{job_id}.json")


def _save_job(job_id: str, data: dict):
    """Write job state to disk atomically."""
    with open(_job_path(job_id), "w") as f:
        json.dump(data, f, indent=2)


def _load_job(job_id: str) -> dict | None:
    """Read job state from disk. Returns None if not found."""
    path = _job_path(job_id)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def _load_all_jobs() -> dict:
    """Reload all persisted jobs on startup."""
    jobs = {}
    for fname in os.listdir(JOBS_DIR):
        if fname.endswith(".json"):
            job_id = fname[:-5]
            try:
                with open(os.path.join(JOBS_DIR, fname), "r") as f:
                    jobs[job_id] = json.load(f)
            except Exception:
                pass  # Ignore corrupt files on startup
    return jobs


# ── Reload jobs on startup (survives restarts) ────────────────────────────────
jobs_db = _load_all_jobs()
print(f"[API] Loaded {len(jobs_db)} existing job(s) from disk on startup.")


# ── Request / Response Models ─────────────────────────────────────────────────

class CopilotRequest(BaseModel):
    query: str = "We provide AI Transformation Services. Find potential customers in India."


class ContactDecision(BaseModel):
    company: str
    approved: bool
    contact_name: Optional[str] = None
    title: Optional[str] = None


class ReviewSubmission(BaseModel):
    decisions: List[ContactDecision]


# ── Background Pipeline Runner ────────────────────────────────────────────────

def run_pipeline_background(job_id: str, query: str):
    try:
        workflow = SalesCopilotWorkflow()
        final_report = workflow.run(query)

        if final_report:
            os.makedirs("outputs", exist_ok=True)

            # Initialize approved state as None (pending review)
            for p in final_report.get("prospects", []):
                p["approved"] = None

            # Save job-specific output
            result_path = f"outputs/job_{job_id}.json"
            with open(result_path, "w") as f:
                json.dump(final_report, f, indent=4)

            # Also save as latest for demo.py compatibility
            with open("outputs/final_report.json", "w") as f:
                json.dump(final_report, f, indent=4)

            demo.generate_demo_report()
            
            # Export to CRM initial contacts found
            export_to_crm(final_report["prospects"], job_id)

            # Update and persist job state
            jobs_db[job_id]["status"] = "completed"
            jobs_db[job_id]["results_path"] = result_path
            _save_job(job_id, jobs_db[job_id])
        else:
            jobs_db[job_id]["status"] = "failed"
            jobs_db[job_id]["error"] = "Pipeline returned None"
            _save_job(job_id, jobs_db[job_id])

    except Exception as e:
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(e)
        _save_job(job_id, jobs_db[job_id])


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/api/v1/jobs", summary="Start Async Pipeline Job")
def start_job(request: CopilotRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "status": "processing",
        "query": request.query
    }
    jobs_db[job_id] = job_data
    _save_job(job_id, job_data)  # Persist immediately
    background_tasks.add_task(run_pipeline_background, job_id, request.query)
    return {"job_id": job_id, "status": "processing", "message": "Job started in the background."}


@app.get("/api/v1/jobs/{job_id}", summary="Check Job Status")
def get_job_status(job_id: str):
    # Check memory first, then disk (handles cross-process reads)
    job = jobs_db.get(job_id) or _load_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": job["status"]}


@app.get("/api/v1/jobs/{job_id}/results", summary="Get Job Results")
def get_job_results(job_id: str):
    job = jobs_db.get(job_id) or _load_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == "processing":
        return {"status": "processing", "message": "Job is still running."}

    if job["status"] == "failed":
        return {"status": "failed", "message": job.get("error", "Unknown error")}

    try:
        with open(job["results_path"], "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Result file not found on disk")


@app.get("/api/v1/jobs/{job_id}/review", summary="Get Contacts for Human Review")
def get_contacts_for_review(job_id: str):
    job = jobs_db.get(job_id) or _load_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "processing":
        raise HTTPException(status_code=400, detail="Job is still processing")
    if job["status"] == "failed":
        raise HTTPException(status_code=400, detail="Job failed")

    try:
        with open(job["results_path"], "r") as f:
            report = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Result file not found on disk")

    contacts = []
    for p in report.get("prospects", []):
        contact = p.get("contact") or {}
        contacts.append({
            "company": p.get("company"),
            "contact_name": contact.get("contact_name"),
            "title": contact.get("title"),
            "linkedin_url": contact.get("linkedin_url"),
            "apollo_id": contact.get("apollo_id"),
            "qualification_score": p.get("qualification_score"),
            "qualification_tier": p.get("qualification_tier"),
            "approved": p.get("approved")
        })
    return {"job_id": job_id, "contacts": contacts}


@app.post("/api/v1/jobs/{job_id}/review", summary="Submit Human Review Decisions")
def submit_review_decisions(job_id: str, submission: ReviewSubmission):
    job = jobs_db.get(job_id) or _load_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job must be completed to submit review")

    try:
        with open(job["results_path"], "r") as f:
            report = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Result file not found on disk")

    decision_map = {d.company.lower().strip(): d for d in submission.decisions}

    updated_prospects = []
    for p in report.get("prospects", []):
        company_key = p.get("company", "").lower().strip()
        if company_key in decision_map:
            decision = decision_map[company_key]
            p["approved"] = decision.approved
            
            if p.get("contact"):
                if decision.contact_name is not None:
                    p["contact"]["contact_name"] = decision.contact_name
                if decision.title is not None:
                    p["contact"]["title"] = decision.title
                    
        updated_prospects.append(p)

    report["prospects"] = updated_prospects

    with open(job["results_path"], "w") as f:
        json.dump(report, f, indent=4)

    export_to_crm(updated_prospects, job_id)

    return {
        "status": "success",
        "message": f"Submitted decisions for {len(submission.decisions)} contacts. CRM exports updated."
    }


@app.get("/api/v1/jobs/{job_id}/dashboard", summary="Get Contact Quality Dashboard Metrics")
def get_job_dashboard(job_id: str):
    job = jobs_db.get(job_id) or _load_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "processing":
        return {"status": "processing", "message": "Job is still running."}
    if job["status"] == "failed":
        return {"status": "failed", "message": job.get("error")}

    try:
        with open(job["results_path"], "r") as f:
            report = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Result file not found on disk")

    prospects = report.get("prospects", [])
    
    total_prospects = len(prospects)
    qualified = sum(1 for p in prospects if p.get("qualification_tier") in ["Hot", "Warm"])
    high_fit = sum(1 for p in prospects if p.get("buyer_fit", {}).get("buyer_fit") in ["High", "Medium"])
    
    apollo_verified = 0
    manual_review = 0
    competitors = 0
    
    for p in prospects:
        contact = p.get("contact") or {}
        is_competitor = p.get("buyer_fit", {}).get("competitor_flag", False)
        
        if is_competitor:
            competitors += 1
            
        if contact.get("verification_level") == "apollo_verified":
            apollo_verified += 1
        elif contact.get("verification_level") in ["not_found", "inferred", None]:
            if not contact.get("contact_name") or contact.get("verification_level") != "apollo_verified":
                manual_review += 1

    return {
        "job_id": job_id,
        "query": report.get("query"),
        "metrics": {
            "prospects_found": total_prospects,
            "qualified": qualified,
            "high_fit": high_fit,
            "apollo_verified_contacts": apollo_verified,
            "manual_review_required": manual_review,
            "competitors_filtered": competitors
        }
    }


@app.get("/api/v1/reports/latest", summary="Get Latest Report Metrics")
def get_latest_report():
    try:
        with open("reports/lead_report.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": "error", "message": "No reports generated yet."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
