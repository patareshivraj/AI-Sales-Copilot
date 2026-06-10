# Codebase Structure Overview — AI Sales Copilot v1.1

This document provides a complete, detailed mapping of the directories and files within the **AI Sales Copilot** repository. It serves as a guide for engineering audits, frontend/backend integration, and developer onboarding.

---

```
AI-Sales-Copilot/
├── agents/                       # Multi-agent logic (Single file = Single agent)
│   ├── buyer_fit_agent.py        # Classifies leads as Customer, Partner, or Competitor
│   ├── company_researcher.py     # Scrapes websites using Trafilatura & BeautifulSoup
│   ├── contact_discovery_agent.py # Searches public sources for decision maker contacts
│   ├── icp_builder.py            # Generates structured ICP Profile from offering description
│   ├── opportunity_agent.py      # Extracts urgency / 'Why Now' signals
│   ├── outreach_agent.py         # Drafts personalized email and LinkedIn templates
│   ├── prospect_finder.py        # Discovers companies using randomized search keywords
│   ├── qualification_agent.py     # Deterministically scores leads (0-100) & details explanation
│   └── sequencer_agent.py        # Generates a 5-step strategic follow-up campaign
│
├── core/                         # Shared infrastructure and orchestration
│   ├── config.py                 # Environment variable configuration (Groq keys, paths)
│   ├── lead_db.py                # Interacts with seen_leads.json for deduplication
│   ├── llm.py                    # LLM Service wrapper with structured output validation
│   ├── orchestrator.py           # Coordinates agents & sequential gates (Safety Gates)
│   └── search_manager.py         # [Legacy] Old search manager (retained for backward compatibility)
│
├── search/                       # Phase 12.1 Reliability Search Layer
│   ├── __init__.py               # Package initializer exposing SearchManager
│   ├── search_manager.py         # Central orchestrator with cache, providers, stale fallback
│   └── providers/                # Search providers directory
│       ├── __init__.py           # Package initializer
│       ├── base_provider.py      # Abstract SearchProvider interface class
│       ├── brave_provider.py     # Brave Search API integration stub
│       └── duckduckgo_provider.py # DuckDuckGo text search provider
│
├── schemas/                      # Data contracts defined using Pydantic models
│   ├── buyer_fit_schema.py       # Pydantic schema for BuyerFitAgent output
│   ├── contact_schema.py         # Pydantic schema for ContactDiscoveryAgent output
│   ├── icp_schema.py             # Pydantic schema for ICPBuilderAgent output
│   ├── opportunity_schema.py     # Pydantic schema for OpportunityAgent output
│   ├── outreach_schema.py        # Pydantic schema for OutreachAgent output
│   ├── prospect_schema.py        # Pydantic schema for ProspectFinderAgent output
│   ├── qualification_schema.py   # Pydantic schema for QualificationAgent output
│   ├── research_schema.py        # Pydantic schema for CompanyResearcherAgent output
│   └── sequencer_schema.py       # Pydantic schema for SequencerAgent output
│
├── evaluation/                   # Automated evaluation & validation suite
│   ├── contact_audit.py          # Runs batch audits to measure contact discovery accuracy
│   ├── run_evaluation.py         # Measures ICP, qualification consistency, and buyer fit precision
│   ├── search_reliability_test.py # Phase 12.1 search layer reliability test suite (4 tests)
│   ├── datasets/                 # Datasets used by evaluation tests
│   └── reports/                  # Generated scorecards (scorecard.json)
│
├── database/                     # SQLite Cache Database
│   └── search_cache.db           # SQLite database for persistent search caching (7-day TTL)
│
├── logs/                         # Observability logs
│   └── search.log                # Search execution metrics and performance log
│
├── outputs/                      # Raw pipeline and orchestrator outputs
│   ├── final_report.json         # Raw result of the latest pipeline execution
│   ├── seen_leads.json           # Deduplication database tracks processed companies
│   └── job_*.json                # Persistent job results from FastAPI runs
│
├── reports/                      # Human-readable documents generated for the user
│   ├── lead_report.md            # Markdown formatted output of qualified/blocked leads
│   ├── lead_report.json          # Formatted JSON report containing leads and metrics
│   └── contacts_found.csv        # Extracted list of verified contacts
│
├── tests/                        # Unit tests per agent
│   ├── test_contact.py           # Unit test for Contact Discovery Agent
│   ├── test_icp.py               # Unit test for ICP Builder Agent
│   ├── test_prospect.py          # Unit test for Prospect Finder Agent
│   ├── test_qualification.py     # Unit test for Lead Scoring / Qualification Agent
│   ├── test_research.py          # Unit test for Company Researcher Agent
│   └── test_sequencer.py         # Unit test for Follow-up Sequencer Agent
│
├── utils/                        # Utility functions
│   └── scraper.py                # Heavyweight web scraper with fallback parsing options
│
├── api.py                        # FastAPI web server with file-based job persistence
├── main.py                       # CLI workflow entrypoint
├── demo.py                       # Script generating formatted demo reports
├── API_INTEGRATION_GUIDE.md      # Integration documentation for API consumers
├── README.md                     # Main project manual, setup instruction, design notes
├── requirements.txt              # Project package dependencies
├── .env                          # Local environment keys configuration (Git ignored)
└── .gitignore                    # Specifies intentionally untracked files to ignore
```

---

## Folder & Component Details

### 1. `agents/` (The Brains)
Each file corresponds to a specialized agent. They are stateless, accepting a Pydantic model input and outputting another Pydantic model validated through Pydantic.
* **`icp_builder.py`**: Reads business description to form a structured profile listing target company size, regions, keywords, and decision makers.
* **`prospect_finder.py`**: Crafts search queries from keywords, then calls `SearchManager` to retrieve prospect URLs.
* **`company_researcher.py`**: Scrapes target website pages and uses LLM to summarize key products, industry context, and pain points.
* **`qualification_agent.py`**: Performs deterministic scoring based on matching criteria and scores signals. Emits explanation reasoning.
* **`buyer_fit_agent.py`**: Segregates competitors and customers to avoid marketing to competitors.
* **`opportunity_agent.py`**: Assesses urgency based on website signals (hiring, fundraising, expanding).
* **`contact_discovery_agent.py`**: Searches web snippets to locate names/roles matching the target ICP decision makers.
* **`outreach_agent.py`**: Writes cold emails and LinkedIn messages using scraped personalization hooks.
* **`sequencer_agent.py`**: Creates a sequence of five follow-up emails, maintaining context.

### 2. `search/` (Phase 12.1 Reliability Search Layer)
Handles external web searches with caching. It isolates DuckDuckGo rate limits.
* **`search_manager.py`**: Implements cache-first loading. If the query is cached and fresh (< 7 days), it returns immediately. If live DDG fails, it checks the database for older (stale) queries, and if all fails, returns an empty list `[]` to prevent system crash.
* **`providers/`**: Pluggable directory of search provider implementations (`base_provider`, `duckduckgo_provider`, `brave_provider`).

### 3. `core/` (Orchestration & State)
* **`llm.py`**: Custom wrapper utilizing Groq Cloud (Llama 3.3 70B) for generating both raw text and structured responses matching a requested Pydantic model.
* **`orchestrator.py`**: Drives the linear agent flow and checks sequential safety gates. If a lead fails any gate (e.g. is identified as a competitor or qualifies below Warm), it is skipped and tagged with a machine-readable `blocked_reason`.

### 4. `evaluation/` (Testing Suite)
Holds automated and deterministic evaluation scripts.
* **`run_evaluation.py`**: Runs evaluations on ICP generation, scoring consistency, and buyer fit precision. Reports are categorized into `automated_test`, `deterministic_test`, and `manual_audit` for transparency.
* **`search_reliability_test.py`**: Tests cache write, cache read, provider failure handling, and stale cache fallback behavior.

### 5. `api.py` (FastAPI Server)
Exposes endpoint routes (`/api/v1/jobs`) for async background job execution. Uses file-based job persistence in the `outputs/` folder (`outputs/job_{id}.json` and `jobs/{id}.json`) to preserve job status and results across restarts.
