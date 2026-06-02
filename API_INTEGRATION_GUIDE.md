# API Integration Guide: AI Sales Copilot

This document is for the **Frontend** and **Backend** engineers integrating the AI Sales Copilot layer. 

Because the AI pipeline performs deep web scraping, LLM analysis, and searches, a single run can take **60-90 seconds**. Therefore, the AI layer now uses an **Asynchronous Job Polling** architecture. The frontend should never wait synchronously for a response.

---

## Architecture Overview for the 3 Engineers

1. **AI Engineer (This Layer)**: Hosts the FastAPI microservice (`api.py`) on a dedicated server or container.
2. **Backend Engineer**: Acts as the middleman. Your Node/Java/Python backend will receive requests from the Frontend, pass them to the AI Layer, store the `job_id` in your database, and periodically poll the AI Layer for completion. Once completed, your backend stores the results in your own database (PostgreSQL/MongoDB).
3. **Frontend Engineer**: Builds the UI (React/Vue/Angular). Sends the initial query to the Backend, displays a loading spinner/progress bar, and polls the Backend until the results are ready to display.

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
2. Create your own endpoints: `POST /api/generate-leads` and `GET /api/generate-leads/:id/status`.
3. When the frontend hits your `POST`, forward the payload to the AI Layer's `POST /api/v1/jobs`. Save the returned `job_id` in your database.
4. Set up a background worker or cron job to poll `GET /api/v1/jobs/{job_id}` every 5-10 seconds.
5. When the status changes to `completed`, fetch the results from `GET /api/v1/jobs/{job_id}/results`, save the JSON payload into your database, and mark the job as done in your system.

## Instructions for Frontend Engineer
1. Build an input field for the "Business Query".
2. When the user clicks "Generate", send the query to your Backend.
3. Your Backend will reply with a Job ID.
4. Show the user a **Loading State**. Explain that "The AI is searching the web and researching companies..." (This takes ~60-90 seconds).
5. Poll your Backend every 3 seconds to check the status.
6. Once the Backend says it's ready, fetch the final JSON and render it in a Dashboard. 

**UI Rendering Tips for Frontend:**
- **Blocked Reason:** If a prospect has a `blocked_reason` (e.g., `COMPETITOR`, `INSUFFICIENT_RESEARCH`, `NO_VERIFIED_CONTACT`), render them in a separate "Manual Review" or "Blocked" table.
- **Outreach:** Only prospects with `blocked_reason: null` will have outreach emails.
- **Score:** Display the `qualification_score` (0-100) prominently.
