# API Integration Guide: AI Sales Copilot

This document is for the **Backend Engineer** integrating the AI Sales Copilot layer. 

Because the AI pipeline performs deep web scraping, LLM analysis, and searches, a single run can take **60-90 seconds**. Therefore, the AI layer uses an **Asynchronous Job Polling** architecture.

---

## Architecture Overview

1. **AI Engineer (This Layer)**: Hosts the FastAPI microservice (`api.py`) on a dedicated server or container.
2. **Backend Engineer**: Acts as the consumer. Your Node/Java/Python backend will receive requests from your own frontend/clients, pass them to the AI Layer, store the `job_id` in your database, and periodically poll the AI Layer for completion. Once completed, your backend stores the results in your own database (PostgreSQL/MongoDB).

---

## The 3 API Endpoints You Need

The AI Layer runs on `http://<ai-server-ip>:8000`.

### 1. Start a New Job
**POST** `/api/v1/jobs`

Starts the multi-agent pipeline in the background and immediately returns a Job ID.

**Request Body:**
```json
{
  "query": "We provide AI Transformation Services. Find potential customers in India."
}
```

**Response (200 OK):**
```json
{
  "job_id": "c8a4b89e-3d84-4e3a-9c92-7f394c5d6e11",
  "status": "processing",
  "message": "Job started in the background."
}
```

---

### 2. Check Job Status (Polling)
**GET** `/api/v1/jobs/{job_id}`

The backend should poll this endpoint every 5 seconds until the status is `completed` or `failed`.

**Response (200 OK):**
```json
{
  "job_id": "c8a4b89e-3d84-4e3a-9c92-7f394c5d6e11",
  "status": "processing" // Can be "processing", "completed", or "failed"
}
```

---

### 3. Get Final Results
**GET** `/api/v1/jobs/{job_id}/results`

Once the status is `completed`, call this to retrieve the massive JSON report containing all prospects, qualification scores, contact discovery, and outreach drafts.

**Response (200 OK):**
```json
{
  "query": "We provide AI Transformation Services...",
  "icp": {
    "industries": ["Finance", "Healthcare"],
    "decision_makers": ["CTO", "CIO"]
  },
  "prospects": [
    {
      "company": "SEESEC",
      "qualification_score": 50,
      "qualification_tier": "Warm",
      "blocked_reason": "NO_VERIFIED_CONTACT",
      "buyer_fit": {
        "buyer_fit": "Medium",
        "competitor_flag": false
      },
      "opportunity": {
        "why_now": ["Hiring AI Engineers"],
        "urgency": "High"
      },
      "contact": {
        "contact_name": null,
        "verification_level": "not_found"
      },
      "outreach": null
    }
  ]
}
```

---

## Instructions for Backend Engineer
1. Do not expose the AI Layer directly to the public internet. Keep it in a private VPC.
2. Create your own endpoints: `POST /api/generate-leads` and `GET /api/generate-leads/:id/status` for your clients.
3. When a request comes in, forward the payload to the AI Layer's `POST /api/v1/jobs`. Save the returned `job_id` in your database.
4. Set up a background worker or cron job to poll `GET /api/v1/jobs/{job_id}` every 5-10 seconds.
5. When the status changes to `completed`, fetch the results from `GET /api/v1/jobs/{job_id}/results`, save the JSON payload into your database, and mark the job as done in your system.
