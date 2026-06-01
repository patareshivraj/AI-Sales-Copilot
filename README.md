# AI Sales Copilot

An open-source AI Sales Copilot designed to assist B2B sales teams. The system leverages a multi-agent architecture to autonomously identify Ideal Customer Profiles (ICPs) and discover highly relevant enterprise prospects using public data and advanced LLMs.

---

## Architecture & Phases

This project is being built in phases to ensure a robust, crash-resistant foundation.

* **Phase 1: Foundation Layer** (Complete)
  * A robust LLM abstraction (`core/llm.py`) utilizing `langchain-groq` and `Pydantic`.
  * Guarantees structured JSON outputs and prevents LLM hallucination crashes.
* **Phase 2: ICP Builder Agent** (Complete)
  * Takes a raw business offering (e.g., "AI Transformation Services") and intelligently deduces the target industries, decision-makers, company size, market type, and search keywords.
* **Phase 3: Prospect Finder Agent** (Complete)
  * Consumes the ICP profile and autonomously queries the web (via DuckDuckGo).
  * Extracts structured lists of real-world companies and assigns a dynamic AI confidence score (0-100) based on how well they match the ICP.
* **Phase 4: Company Research Agent** (Complete)
  * Scrapes public website content to extract services, industry context, AI readiness, and pain points without hallucination.
* **Phase 5 & Beyond**: (In Development) Lead Qualification, and Automated Outreach Drafting.

---

## Technology Stack

* **Language**: Python 3
* **LLM Orchestration**: LangChain, LangGraph
* **Inference**: Groq API (High-speed Llama-3 generation)
* **Data Validation**: Pydantic
* **Search / Data Sourcing**: DuckDuckGo Search (`ddgs`)
* **Web Scraping**: Requests, BeautifulSoup4

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/patareshivraj/AI-Sales-Copilot.git
cd AI-Sales-Copilot
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
# On Windows
.\.venv\Scripts\activate
# On Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

---

## Running the Tests

The system is highly test-driven. You can validate the agents using the built-in test scripts:

**Test the LLM Abstraction Layer:**
```bash
python validation_tests.py
```

**Test the ICP Builder Agent:**
```bash
python tests/test_icp.py
```

**Test the Prospect Finder Agent:**
```bash
python tests/test_prospect.py
```

**Test the Company Researcher Agent:**
```bash
python tests/test_research.py
```

---

## Design Philosophy

1. **No Hallucinations**: We enforce strict schema parsing using Pydantic. If an input is invalid, the system gracefully populates an `error` field rather than guessing.
2. **Deterministic Handoffs**: Agents do not chat with each other in an open-ended way. Data flows via tightly typed JSON objects.
3. **Public Data Only**: The copilot strictly operates on publicly accessible search and website data. No private scraping or authenticated bypasses are utilized.
