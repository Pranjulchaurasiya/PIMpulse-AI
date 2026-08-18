# ⚡ PIMpulse AI — Autonomous Industrial Product Enrichment & MDM Engine
> **UniHack 2026 Submission** | *Enterprise-Grade Product Data Standardization, 253-Column Schema Delivery & Agentic Web Grounding*

---

## 🌟 Executive Summary

**PIMpulse AI** is an autonomous, high-throughput Master Data Management (MDM) and Agentic RAG engine engineered specifically for industrial B2B commerce (Unilog standard). It accepts messy, unstandardized product strings or raw spreadsheets (`.csv` / `.xlsx`) and transforms them into **100% compliant, 253-column verified product profiles** with zero hallucination.

```
                              [ Incoming Product Query / Spreadsheet ]
                                                 │
                                        Is it bulk/structured?
                                       ┌─────────┴─────────┐
                                       ▼                   ▼
                        [ TIER 1: MDM RULE ENGINE ]  [ TIER 2: LANGGRAPH AGENT PIPELINE ]
                        • Polars Columnar Parser     • HyDE Hypothesis Generation
                        • RapidFuzz LOV Matcher      • Live Tavily Web Search
                        • Word-Boundary Truncator    • Groq LPU / LLM Extraction
                        • 253-Column Schema Appender • Grounding & Provenance Gate
                                       │                   │
                             ⚡ 190 SKUs/sec          ⏱️ 8–12 sec/SKU
```

---

## 🏆 Key Capabilities & Compliance

1. **Official 253-Column Unilog Master Delivery Standard**:
   * Complete 50 attribute triplets (`ATTRIBUTE_LABEL 1..50`, `ATTRIBUTE_VALUE 1..50`, `ATTRIBUTE_UOM 1..50`).
   * Native text `@` cell formatting in Excel (`.xlsx`) to prevent fraction-to-date corruption (`4-1/2`, `7/8`).
   * UTF-8 with BOM (`utf-8-sig`) in CSV to preserve special symbols (`®`, `™`, `¼`, `½`, `¾`).

2. **100.0% Mathematical Compliance on Length Invariants**:
   * `INVOICE_DESC`: Strictly bounded to **$\le 40$ characters**, ALL CAPS, with **word-boundary truncation** (no mid-word slicing).
   * `MOBILE_DESC`: Strictly bounded in **$[60, 80]$ characters** with dynamic attribute padding.

3. **Shared Workbook Ingestion Model**:
   * Upload any `.xlsx` spreadsheet; PIMpulse AI preserves original sheets and appends the **`Enriched_Output`** worksheet directly into the same workbook.

4. **Zero-Hallucination Grounding Gate**:
   * Extracted attributes are verified against OEM technical datasheets and domain allowlists.
   * If an unseen/unknown part has no online proof, it gracefully outputs empty grounded attributes with an unclassified status (Zero guessing).

5. **Interactive Data Lineage & Provenance UI**:
   * Every attribute in the web dashboard is clickable, displaying verbatim quotes, source URLs, and mathematical confidence allocations.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Agentic Framework** | **LangGraph v0.2 + LangChain** (State-machine graph with grounding gates) |
| **LLM & Inference** | **Groq LPUs** (`llama-3.1-8b-instant` / `llama-3.3-70b-versatile` @ $0.0006/SKU) |
| **Live Web Retrieval** | **Tavily Search API** (Domain-restricted OEM crawling) |
| **Data Processing** | **Polars (Rust-backed)** + **RapidFuzz (C++)** + **OpenPyXL** |
| **Backend & API** | **FastAPI + Uvicorn** (ASGI REST + Server-Sent Events SSE) |
| **Frontend UI** | **Vanilla HTML5/CSS3/JS** (Glassmorphism Dark Mode SPA) |
| **Testing** | **Pytest + Pytest-Asyncio** (19 / 19 passing tests) |

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Install Dependencies
```bash
git clone <your-repo-url>
cd "PIMpulse AI"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and enter your API keys:
```bash
cp .env.example .env
```
```ini
PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here
TAVILY_API_KEY=tvly-your_tavily_api_key_here
```

### 3. Start the Server
```bash
python main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 🧪 Running Automated Tests

Run the full 19-test suite (smoke tests, invariant compliance, and stress simulations):
```bash
python -m pytest tests/test_smoke.py test_comprehensive_suite.py test_stress_and_evaluator_simulation.py
```

---

## 📁 Repository Structure

```
├── agents/                  # LangGraph nodes & deterministic MDM rule engines
│   ├── extraction.py        # LLM extraction & schema validation
│   ├── retrieval.py         # Tavily live search & RRF multi-source fusion
│   ├── unilog_pipeline.py   # 253-column generator & shared workbook appender
│   └── unilog_rules.py      # Canonical brand dictionary & length limit enforcers
├── data/                    # Master industrial reference seeds (25 categories)
├── llm/                     # Groq LPU client & cost tracker
├── rules/                   # UNSPSC taxonomy & material LOV schemas
├── static/                  # Single Page Application (HTML5/CSS3/JS)
├── tests/                   # Automated pytest suites
├── .env.example             # Environment template (API keys omitted)
├── .gitignore               # Comprehensive Git ignore rules
├── benchmark_unilog_1000.py # High-speed Polars batch benchmark
├── graph.py                 # LangGraph state machine & router
├── main.py                  # FastAPI application & SSE endpoints
├── requirements.txt         # Production dependencies
├── zerops.yaml              # Zerops cloud deployment recipe
└── README.md                # Project documentation
```

---

## 👥 Authors & License
Developed for **UniHack 2026**. Licensed under the MIT License.
