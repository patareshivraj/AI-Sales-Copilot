# AI Sales Copilot

An enterprise-grade, open-source, multi-agent AI system that automates the entire B2B sales intelligence pipeline: from Ideal Customer Profile generation to prospect discovery, company research, lead qualification, buyer fit evaluation, opportunity timing analysis, contact discovery, personalized outreach drafting, and follow-up sequence generation.

Built with a strict engineering philosophy: deterministic scoring, zero hallucination tolerance, and explainable outputs at every stage.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Pipeline Overview](#pipeline-overview)
- [Agent Registry](#agent-registry)
- [Schema Registry](#schema-registry)
- [Project Structure](#project-structure)
- [Setup and Configuration](#setup-and-configuration)
- [Running the System](#running-the-system)
- [API Reference](#api-reference)
- [Evaluation Framework](#evaluation-framework)
- [Design Philosophy](#design-philosophy)
- [Safety Mechanisms](#safety-mechanisms)
- [Known Limitations](#known-limitations)
- [Remaining Work and Roadmap](#remaining-work-and-roadmap)
- [Technology Stack](#technology-stack)

---

## System Architecture

The system implements a sequential, gate-controlled pipeline. Each agent receives strictly typed Pydantic input, performs its task, and emits strictly typed Pydantic output. No agent communicates with another agent directly. All data flows through the central orchestrator.

### High-Level Agent Pipeline

```mermaid
graph TD
    A["User Query"] --> B["ICP Builder Agent"]
    B -->|"Structured ICP JSON"| C["Prospect Finder Agent"]
    C -->|"Company Names + URLs"| D["Company Research Agent"]
    D -->|"Scraped Intelligence"| E["Qualification Agent"]
    E -->|"Deterministic Score"| F["Buyer Fit Agent"]
    F -->|"Customer / Competitor / Partner"| G["Opportunity Intelligence Agent"]
    G -->|"Why Now Signals"| H["Gate Controller"]
    H -->|"Passed All Gates"| I["Contact Discovery Agent"]
    I -->|"Verified Contact"| J["Outreach Agent"]
    J -->|"Cold Email + LinkedIn"| K["Follow-Up Sequencer"]
    K --> L["Final Report"]

    subgraph "Core Abstraction"
        LLM["LLM Service (core/llm.py)"]
    end

    B -.->|"generate_structured()"| LLM
    D -.->|"generate_structured()"| LLM
    E -.->|"Reasoning Only"| LLM
    F -.->|"Classification"| LLM
    G -.->|"Signal Analysis"| LLM
    I -.->|"Contact Extraction"| LLM
    J -.->|"Email Drafting"| LLM
    K -.->|"Sequence Generation"| LLM

    style LLM fill:#1a1a2e,stroke:#e94560,color:#fff
    style L fill:#0f3460,stroke:#e94560,color:#fff
    style A fill:#16213e,stroke:#0f3460,color:#fff
```

### Gate-Controlled Decision Flowchart

Every prospect passes through a series of sequential gates. Failure at any gate blocks outreach and tags the prospect with a machine-readable `blocked_reason` code.

```mermaid
flowchart TD
    START["Prospect Researched and Qualified"] --> G1{"Research Sufficient?"}

    G1 -->|"No"| B1["BLOCKED: INSUFFICIENT_RESEARCH"]
    G1 -->|"Yes"| G2{"Qualification Tier?"}

    G2 -->|"Cold"| B2["BLOCKED: COLD_PROSPECT"]
    G2 -->|"Warm / Hot"| G3{"Competitor?"}

    G3 -->|"Yes"| B3["BLOCKED: COMPETITOR"]
    G3 -->|"No"| G4{"Buyer Fit Allowed?"}

    G4 -->|"No"| B4["BLOCKED: LOW_BUYER_FIT"]
    G4 -->|"Yes"| CD["Contact Discovery Agent"]

    CD --> G5{"Verified Contact Found?"}

    G5 -->|"No"| B5["BLOCKED: NO_VERIFIED_CONTACT"]
    G5 -->|"Yes"| OA["Outreach Agent"]

    OA --> SEQ["Follow-Up Sequencer"]
    SEQ --> REPORT["Final Report Generated"]

    B1 --> MR["Manual Review Queue"]
    B2 --> MR
    B3 --> MR
    B4 --> MR
    B5 --> MR

    style B1 fill:#e94560,stroke:#1a1a2e,color:#fff
    style B2 fill:#e94560,stroke:#1a1a2e,color:#fff
    style B3 fill:#e94560,stroke:#1a1a2e,color:#fff
    style B4 fill:#e94560,stroke:#1a1a2e,color:#fff
    style B5 fill:#e94560,stroke:#1a1a2e,color:#fff
    style REPORT fill:#0f3460,stroke:#e94560,color:#fff
    style MR fill:#533483,stroke:#e94560,color:#fff
    style OA fill:#16213e,stroke:#0f3460,color:#fff
    style SEQ fill:#16213e,stroke:#0f3460,color:#fff
    style CD fill:#16213e,stroke:#0f3460,color:#fff
```

### Data Flow Between Schemas

```mermaid
graph LR
    A["ICPProfile"] -->|"industries, keywords, market_type"| B["ProspectList"]
    B -->|"company, website"| C["CompanyResearch"]
    C -->|"industry, signals, ai_readiness"| D["Qualification"]
    A -->|"industries"| D
    C -->|"services, industry"| E["BuyerFit"]
    C -->|"signals, pain_points"| F["OpportunityIntelligence"]
    D -->|"score, tier, reasoning"| F
    A -->|"decision_makers"| G["Contact"]
    C -->|"signals, pain_points"| H["Outreach"]
    D -->|"reasoning"| H
    H -->|"cold_email"| I["FollowUpSequence"]
    C -->|"services, signals"| I

    style A fill:#1a1a2e,stroke:#e94560,color:#fff
    style D fill:#0f3460,stroke:#e94560,color:#fff
    style E fill:#533483,stroke:#e94560,color:#fff
    style G fill:#16213e,stroke:#0f3460,color:#fff
    style H fill:#16213e,stroke:#0f3460,color:#fff
```

No outreach is ever generated for a blocked prospect. Every blocked prospect carries an auditable reason code.

---

## Pipeline Overview

The pipeline is organized into phases. Each phase was built, tested, and validated independently before being integrated into the orchestrator.

| Phase | Module | Purpose | Input | Output |
|---|---|---|---|---|
| 1 | LLM Abstraction Layer | Centralizes all LLM calls with Pydantic structured output enforcement | API Keys, Model Config | Crash-resistant LLM Service |
| 2 | ICP Builder Agent | Derives target industries, company sizes, decision-maker titles, regions, and search keywords from a raw business offering | Free-text business description | Structured ICP Profile |
| 3 | Prospect Finder Agent | Searches DuckDuckGo using randomized ICP-derived keywords to discover fresh companies | ICP Profile | List of company names and URLs |
| 4 | Company Research Agent | Scrapes company websites via HTTP, cleans HTML, and uses the LLM to extract structured business intelligence | Company URL | Industry, services, signals, AI readiness, pain points |
| 5 | Qualification Agent | Calculates a deterministic lead score using a rules engine, then uses the LLM solely to explain the score | ICP + Research | Score (0-100), Tier (Hot/Warm/Cold), Score Breakdown |
| 5.5 | Buyer Fit Agent | Classifies the prospect as Potential Customer, Competitor, or Partner | Business offering + ICP + Research | Buyer type, competitor flag, outreach_allowed |
| 6 | Orchestrator & State Manager | Connects all agents into a pipeline. Uses `LeadDatabase` to filter out previously seen prospects, ensuring fresh leads on every run | User query | End-to-end report |
| 7 | Outreach Agent | Drafts a personalized cold email and LinkedIn message grounded in research signals | Research + Qualification | Email, LinkedIn message, personalization reason |
| 8 | Follow-Up Sequencer | Generates a 5-step follow-up campaign with distinct strategic angles per email | Research + Initial Outreach | 5 follow-up emails (Insight, Pain Point, Case Study, Value Recap, Breakup) |
| 9 | Evaluation Framework | Measures ICP accuracy, qualification consistency, buyer fit precision, and hallucination rate | Test datasets | Scorecard JSON |
| 10.5 | Contact Discovery Agent | Searches public sources for decision-maker names and LinkedIn profiles | Company name + ICP decision-maker titles | Contact name, title, LinkedIn URL, confidence |
| 12 | Opportunity Intelligence | Analyzes research signals to answer "Why should we target this company right now?" | Research + Qualification | Why Now reasons, urgency level, recommended sales angle |

---

## Agent Registry

Every agent in the system is a standalone Python class with a single public method. Agents are located in the `agents/` directory.

| Agent | File | Method | LLM Usage | Deterministic Logic |
|---|---|---|---|---|
| ICP Builder | `agents/icp_builder.py` | `build_icp(query)` | Structured output generation | None |
| Prospect Finder | `agents/prospect_finder.py` | `find_prospects(icp, limit)` | Structured output parsing of search results | Query randomization for fresh leads |
| Company Researcher | `agents/company_researcher.py` | `research_company(name, url)` | Content analysis from scraped HTML | HTTP scraping, HTML cleaning |
| Qualification Agent | `agents/qualification_agent.py` | `qualify(icp, research)` | Reasoning explanation only | Full score calculation (industry match + AI readiness + signals) |
| Buyer Fit Agent | `agents/buyer_fit_agent.py` | `evaluate(offering, icp, research)` | Competitor/partner/customer classification | outreach_allowed and disqualification_reason enforcement |
| Opportunity Agent | `agents/opportunity_agent.py` | `analyze(research, qualification)` | Why-now signal extraction | Urgency gating for insufficient research |
| Contact Discovery | `agents/contact_discovery_agent.py` | `find_contact(company, icp)` | Contact extraction from search snippets | Source attribution, confidence scoring |
| Outreach Agent | `agents/outreach_agent.py` | `draft_outreach(research, qualification)` | Email and LinkedIn message generation | None |
| Sequencer Agent | `agents/sequencer_agent.py` | `generate_sequence(research, outreach)` | 5-step follow-up generation | None |

---

## Schema Registry

All data contracts are defined as Pydantic models in the `schemas/` directory. Every field includes a description. No agent accepts or returns untyped data.

| Schema | File | Key Fields |
|---|---|---|
| ICP Profile | `schemas/icp_schema.py` | industries, company_size, decision_makers, regions, market_type, keywords |
| Prospect | `schemas/prospect_schema.py` | company, website, confidence, matched_keywords |
| Company Research | `schemas/research_schema.py` | industry, summary, services, pain_points, signals (type + confidence), ai_readiness |
| Qualification | `schemas/qualification_schema.py` | score, tier, score_breakdown (industry_match, ai_readiness, signals), reasoning |
| Buyer Fit | `schemas/buyer_fit_schema.py` | buyer_fit, buyer_type, competitor_flag, partner_flag, outreach_allowed, disqualification_reason |
| Opportunity | `schemas/opportunity_schema.py` | why_now, urgency, recommended_angle |
| Contact | `schemas/contact_schema.py` | contact_name, title, linkedin_url, email, verification_level, source_url, contact_confidence |
| Outreach | `schemas/outreach_schema.py` | subject, cold_email, linkedin_message, personalization_reason |
| Follow-Up Sequence | `schemas/sequencer_schema.py` | follow_up_1 through follow_up_5 (Insight, Pain Point, Case Study, Value Recap, Breakup) |

---

## Project Structure

```
sales-copilot/
|
|-- agents/
|   |-- icp_builder.py
|   |-- prospect_finder.py
|   |-- company_researcher.py
|   |-- qualification_agent.py
|   |-- buyer_fit_agent.py
|   |-- opportunity_agent.py
|   |-- contact_discovery_agent.py
|   |-- outreach_agent.py
|   |-- sequencer_agent.py
|
|-- core/
|   |-- llm.py                  # LLM abstraction layer
|   |-- config.py               # Centralized configuration
|   |-- orchestrator.py         # Pipeline orchestrator with gate logic
|   |-- lead_db.py              # Local JSON state management for de-duplication
|
|-- schemas/
|   |-- icp_schema.py
|   |-- prospect_schema.py
|   |-- research_schema.py
|   |-- qualification_schema.py
|   |-- buyer_fit_schema.py
|   |-- opportunity_schema.py
|   |-- contact_schema.py
|   |-- outreach_schema.py
|   |-- sequencer_schema.py
|
|-- evaluation/
|   |-- datasets/               # Test datasets for benchmarking
|   |-- reports/                # Generated scorecards
|   |-- run_evaluation.py       # Automated evaluation script
|   |-- contact_audit.py        # Contact discovery audit (10 companies)
|
|-- tests/
|   |-- test_icp.py
|   |-- test_prospect.py
|   |-- test_research.py
|   |-- test_qualification.py
|   |-- test_sequencer.py
|   |-- test_contact.py
|
|-- reports/                    # Generated demo reports
|   |-- lead_report.md
|   |-- lead_report.json
|   |-- contacts_found.csv
|
|-- outputs/                    # Raw pipeline output
|   |-- final_report.json
|
|-- api.py                      # FastAPI server with Swagger UI
|-- main.py                     # CLI pipeline runner
|-- demo.py                     # Demo report generator
|-- requirements.txt
|-- .env
```

---

## Setup and Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/patareshivraj/AI-Sales-Copilot.git
cd AI-Sales-Copilot
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install fastapi uvicorn
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
MODEL_NAME=llama-3.3-70b-versatile
```

---

## Running the System

### Option A: CLI Pipeline

Runs the full pipeline and saves a JSON report to `outputs/final_report.json`:

```bash
python main.py
```

### Option B: API with Swagger UI

Starts a FastAPI server with interactive documentation:

```bash
python api.py
```

Then open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser.

Available endpoints:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/run` | Triggers the full pipeline with a custom query |
| GET | `/api/v1/reports/latest` | Returns the latest report metrics |

### Option C: Demo Report

Generates human-readable reports from the latest pipeline output:

```bash
python demo.py
```

Outputs: `reports/lead_report.md`, `reports/lead_report.json`, `reports/contacts_found.csv`

---

## API Reference

### POST /api/v1/run

Request body:

```json
{
  "query": "We provide AI Transformation Services. Find potential customers in India."
}
```

Response structure (per prospect):

```json
{
  "company": "ABC Manufacturing",
  "qualification_score": 75,
  "qualification_tier": "Hot",
  "blocked_reason": null,
  "buyer_fit": { "buyer_type": "Potential Customer", "competitor_flag": false },
  "opportunity": { "why_now": ["Hiring AI Engineers", "Expanding digital ops"], "urgency": "High" },
  "contact": { "contact_name": "Jane Doe", "title": "CTO", "linkedin_url": "..." },
  "outreach": { "subject": "...", "cold_email": "...", "linkedin_message": "..." },
  "sequence": { "follow_up_1_insight": "...", "follow_up_5_breakup": "..." }
}
```

Blocked reason codes:

| Code | Meaning |
|---|---|
| `INSUFFICIENT_RESEARCH` | Website scrape failed or returned no usable content |
| `COLD_PROSPECT` | Qualification score too low to justify outreach |
| `COMPETITOR` | Buyer Fit Agent identified overlapping services |
| `LOW_BUYER_FIT` | Company does not match ICP as a buyer |
| `NO_VERIFIED_CONTACT` | No decision maker found via public search |
| `null` | All gates passed; outreach was generated |

---

## Evaluation Framework

The evaluation suite measures system reliability across multiple dimensions.

Run the evaluation:

```bash
python evaluation/run_evaluation.py
```

Run the contact discovery audit:

```bash
python evaluation/contact_audit.py
```

### Metrics Tracked

| Metric | What It Measures | Target |
|---|---|---|
| ICP Accuracy | Do generated industries match expected targets? | Above 80% |
| Qualification Consistency | Does the same prospect receive the same score across runs? | Variance near zero |
| Buyer Fit Precision | Are competitors correctly identified as competitors? | Above 85% |
| Research Accuracy | Is the extracted industry correct when verified manually? | Above 90% |
| Hallucination Rate | How often does the system fabricate unsupported claims? | Below 5% |
| Outreach Grounding | Do outreach emails reference actual research data? | 100% |

### Latest Scorecard

```json
{
    "icp_accuracy": 100.0,
    "qualification_consistency": 100.0,
    "buyer_fit_precision": 100.0,
    "research_accuracy": 92.0,
    "hallucination_rate": 0.0,
    "outreach_grounding": 100.0
}
```

---

## Design Philosophy

### 1. Deterministic Scoring, Not LLM Intuition

Qualification scores are calculated in Python using explicit rules (industry match = 30 points, AI readiness = up to 40 points, signals = up to 30 points). The LLM is only used to explain the pre-calculated score in natural language. This makes scores auditable, reproducible, and debuggable.

### 2. Zero Hallucination Tolerance

When a website blocks access via WAF or Captcha, the system returns `"status": "Insufficient information"` instead of fabricating company data. When Contact Discovery fails, it returns `"verification_level": "not_found"` instead of guessing email addresses.

### 3. Strict Schema Contracts

Every agent input and output is a Pydantic model. This eliminates ambiguous data handoffs between pipeline stages and guarantees that downstream agents always receive the fields they expect.

### 4. Gate-Controlled Outreach

Outreach is never generated blindly. Every prospect must pass through five sequential gates (research quality, qualification tier, competitor check, buyer fit, verified contact) before the system writes a single word of email copy.

### 5. State Management & De-duplication

The system implements a local `LeadDatabase` (`outputs/seen_leads.json`) to persist state across runs. Once a company is processed, it is marked as seen. Combined with dynamic keyword randomization in the Prospect Finder, this mathematically guarantees that the system will never process the same lead twice, solving the problem of short-term static search engine results.

### 6. Public Data Only

The system operates exclusively on publicly accessible data sources. No private APIs, no authenticated scraping, no LinkedIn login bypass.

---

## Safety Mechanisms

| Mechanism | Where It Applies | What It Prevents |
|---|---|---|
| Pydantic Schema Enforcement | All agents | Malformed or missing fields in data handoffs |
| Research Failure Detection | Company Researcher | Hallucinating company data when scrape fails |
| Competitor Flagging | Buyer Fit Agent | Sending sales emails to direct competitors |
| Outreach Gate | Orchestrator | Generating outreach for unqualified or uncontactable prospects |
| Contact Verification Level | Contact Discovery | Fabricating email addresses or LinkedIn URLs |
| Blocked Reason Codes | Orchestrator | Ensures every skipped prospect has an auditable reason |
| Score Breakdown | Qualification Agent | Makes the scoring logic fully transparent and debuggable |

---

## Known Limitations

These are engineering constraints, not bugs. Each is understood and documented.

| Limitation | Root Cause | Impact | Mitigation Path |
|---|---|---|---|
| Contact discovery rate is approximately 10% | Free DuckDuckGo search is heavily rate-limited and rarely surfaces executive profiles | Most prospects are tagged `NO_VERIFIED_CONTACT` and require manual review | Integrate Apollo.io, Hunter.io, or Clearbit API for production-grade contact enrichment |
| Email verification is not supported | Public search results almost never expose verified executive email addresses | `email` field returns `null` for all contacts | Requires a dedicated email verification service (Hunter, ZeroBounce) |
| Prospect discovery depends on search engine availability | DuckDuckGo occasionally rate-limits or returns DNS errors | Some pipeline runs discover fewer prospects than expected | Add retry logic, implement search provider fallback, or use a paid search API |
| Industry classification can be imprecise | Company websites do not always state their industry explicitly | Some prospects may receive `industry: null`, affecting the qualification score | Cross-reference with industry databases or business registries |
| No CRM integration | Out of scope for POC | Qualified leads must be manually exported via CSV | Build CRM sync module (Salesforce, HubSpot) in a future phase |

---

## Remaining Work and Roadmap

The following sections describe what has not yet been built, why it matters, and the recommended priority order.

### Priority 1: Enterprise Contact Enrichment

**What**: Replace the current DuckDuckGo-based contact discovery with an enterprise API (Apollo.io, Hunter.io, or Clearbit).

**Why it matters**: The contact discovery audit showed a 10% success rate using free public search. This is not an AI problem; it is a data availability problem. The agent logic is correct and does not hallucinate contacts. The data source is simply too weak for production use. Enterprise contact APIs would push this rate above 80%.

**Effort**: Low. The `ContactDiscoveryAgent` interface is already defined. The change is limited to swapping the DuckDuckGo search call with an API call and parsing the response into the existing `Contact` schema.

### Priority 2: Email Verification Layer

**What**: Add a verification step after contact discovery that confirms the discovered email address is deliverable.

**Why it matters**: Even with Apollo or Hunter, email addresses can be outdated or invalid. Sending to invalid addresses damages sender reputation and domain deliverability scores. A verification layer (using ZeroBounce, NeverBounce, or Hunter's built-in verification) would add a `verification_status: "deliverable" | "risky" | "invalid"` field.

**Effort**: Low. This is a single API call inserted between contact discovery and outreach generation.

### Priority 3: LangGraph Migration

**What**: Replace the current linear Python orchestrator (`core/orchestrator.py`) with a LangGraph state machine.

**Why it matters**: The current orchestrator is a straightforward `if/else` pipeline. It works perfectly for the current linear workflow. However, LangGraph would enable conditional branching (e.g., re-researching a prospect if confidence is low), parallel execution (researching multiple prospects simultaneously), human-in-the-loop approval gates, and persistent state checkpointing. These are valuable for production but unnecessary for a POC.

**Effort**: Medium. The agent interfaces are already clean and decoupled. Migration would involve defining a LangGraph state schema and wiring existing agent methods as graph nodes.

### Priority 4: Human Approval Workflow

**What**: Add a human review step before outreach is sent. A reviewer would see the research, qualification, buyer fit, and opportunity intelligence, then approve or reject the outreach.

**Why it matters**: Even with all safety gates, a human reviewer catches edge cases that automated systems miss (e.g., a company that is technically not a competitor but shares a key investor). This is standard practice in enterprise sales automation.

**Effort**: Medium. Requires a simple web interface or Slack integration for approval routing.

### Priority 5: CRM Integration

**What**: Automatically push qualified leads, research data, and outreach drafts into Salesforce, HubSpot, or Pipedrive.

**Why it matters**: Without CRM sync, the output of the pipeline lives in JSON files. Sales teams do not work in JSON. They work in CRM dashboards. Pushing data directly into the CRM eliminates manual data entry and ensures leads are immediately actionable.

**Effort**: Medium. Requires OAuth setup and field mapping for the target CRM.

### Priority 6: Multi-Provider LLM Support

**What**: Extend `core/llm.py` to support Ollama (local models), OpenAI, and Anthropic in addition to Groq.

**Why it matters**: The LLM abstraction layer was explicitly designed for this. Agents call `llm.generate()` and `llm.generate_structured()` without knowing which provider is behind the call. Adding Ollama support would enable fully offline, air-gapped operation for enterprises with strict data policies.

**Effort**: Low. The abstraction layer already exists. Each new provider requires implementing the same interface.

### Priority 7: Batch Processing and Rate Limit Management

**What**: Add a queuing system that processes large prospect lists without hitting Groq or DuckDuckGo rate limits.

**Why it matters**: The current system processes prospects sequentially with no rate-limit awareness. At scale (50+ prospects), this will hit API limits. A batch processor with exponential backoff and configurable concurrency would make the system production-resilient.

**Effort**: Medium. Requires async processing and a retry/backoff mechanism.

### Not Planned (and Why)

| Feature | Reason for Exclusion |
|---|---|
| LinkedIn Automation (Auto-connect, Auto-message) | Violates LinkedIn Terms of Service. Would expose users to account bans. |
| Automated Email Sending | Sending emails without human review is irresponsible in a sales context. The system generates drafts, not sends. |
| Real-time Web Scraping at Scale | Free scraping is fragile and legally ambiguous. Enterprise data providers are the correct solution. |
| Fine-tuning a Custom LLM | Unnecessary. The system achieves 100% qualification consistency and 0% hallucination rate using prompt engineering and deterministic logic alone. |

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| LLM Provider | Groq (Llama 3.3 70B Versatile) |
| LLM Orchestration | LangChain |
| Data Validation | Pydantic |
| Web Search | DuckDuckGo Search (ddgs) |
| Web Scraping | Requests, BeautifulSoup4 |
| API Layer | FastAPI, Uvicorn |
| Configuration | python-dotenv |

---

## License

This project is open-source and available under the MIT License.
