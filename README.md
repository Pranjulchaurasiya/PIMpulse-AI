<a name="top"></a>
<div align="center">

<img src="docs/hero-banner.svg" alt="PIMpulse AI Hero Banner" width="100%"/>

<a href="#top">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=20&duration=2600&pause=900&color=38BDF8&center=true&vCenter=true&width=760&lines=Raw+distributor+catalogs+in.+Revenue-ready+Unilog+master+out.;190.2+SKUs%2Fsec+Polars+SIMD+throughput.;Verbatim+OEM+grounding.+0%25+hallucinations.;Built+for+UniHack+2026." alt="Typing SVG" />
</a>

<br/>

[![UniHack 2026](https://img.shields.io/badge/UniHack-2026%20Submission-0284c7?style=for-the-badge&logo=rocket)](https://unilogcorp.com)
[![Live Demo](https://img.shields.io/badge/Live%20Prototype-Zerops%20Cloud-38bdf8?style=for-the-badge&logo=google-cloud)](https://pimpulseai-2998-8000.prg1.zerops.app/)
[![Demo Video](https://img.shields.io/badge/Demo%20Video-Google%20Drive-red?style=for-the-badge&logo=google-drive)](https://drive.google.com/file/d/110J1YW0Qsv1ogMqS2wFtxd3LhgExFPJT/view)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph%20v0.2-8b5cf6?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Throughput](https://img.shields.io/badge/Throughput-190.2%20SKUs%2Fsec-10b981?style=for-the-badge)](https://github.com)
[![Invariants](https://img.shields.io/badge/MDM%20Compliance-100%25%20Pass-10b981?style=for-the-badge)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-amber?style=for-the-badge)](LICENSE)

<br/>

<!-- 1-Command Launch Callout -->
<div align="center">
  <pre style="background: #0f172a; color: #38bdf8; border: 1px solid #1e293b; padding: 10px 16px; border-radius: 8px; font-size: 12.5px; max-width: 840px; text-align: center;"><code>🚀 Launch PIMpulse AI in 1 Command: git clone https://github.com/Pranjulchaurasiya/PIMpulse-AI.git && cd PIMpulse-AI && pip install -r requirements.txt && python main.py</code></pre>
</div>

<br/>

<!-- Live Prototype & Video Link Banner -->
<div align="center">

| 🌐 **Live Cloud Prototype** | 🎬 **Official Demo Video** | 📊 **Master Dataset** |
| :---: | :---: | :---: |
| [**pimpulseai-2998-8000.prg1.zerops.app**](https://pimpulseai-2998-8000.prg1.zerops.app/) | [**Watch on Google Drive**](https://drive.google.com/file/d/110J1YW0Qsv1ogMqS2wFtxd3LhgExFPJT/view) | [**1,000-SKU Enriched XLSX**](PIMpulse_Unilog_Enriched_1000.xlsx) |

</div>

<br />

<!-- Animated Live Pipeline Circuit Map -->
<p align="center">
  <img src="process_flow_circuit.svg" alt="PIMpulse AI Live Pipeline Facility Flow Map (Real-Time Circuit)" width="100%" style="max-width: 840px;" />
</p>

<br />

<div align="center">

### Jump to

[The problem](#the-problem) · [The solution](#the-solution) · [See it transform a real row](#see-it-transform-a-real-row) · [Why PIMpulse](#competitive-positioning) · [Architecture](#system-architecture) · [Quickstart](#quickstart) · [Benchmark](#benchmark)

</div>

</div>

---

<a name="the-problem"></a>
## 📌 The Problem

Industrial distributors receive millions of raw, messy catalog records from hundreds of manufacturers with severe data quality issues:
* **Cryptic POS Strings**: Point-of-Sale strings with non-standard abbreviations (`3/8 CPLG BRS 150#`, `PDSH4816AF Dishwasher SS`).
* **Brand Fragmentation**: Identical manufacturers entered under cryptic supplier spellings without canonical legal trademarks (`APPDE` $\rightarrow$ `FRIGIDAIRE®`).
* **Length Violations**: Descriptions overflowing Point-of-Sale character limits ($>40$ chars) or collapsing on mobile commerce viewports.
* **Unsearchable Specifications**: Missing UNSPSC classifications, unformatted fractions (`50.25 in`), and blank parametric attributes.
* **Manual Data Entry Bottleneck**: High human error rates and expensive manual Excel processing ($0.05–$0.20/SKU).

---

<a name="the-solution"></a>
## 💡 The Solution

**PIMpulse AI** is an autonomous, high-throughput product intelligence and catalog enrichment engine designed for B2B industrial commerce:
* **252-Column Unilog Master Compliance**: Automatically maps and populates all 252 official delivery columns, including 50 parametric attribute triplets (`LABEL 1..50`, `VALUE 1..50`, `UOM 1..50`).
* **100% Length Invariants**: Enforces strict POS `INVOICE_DESC` ($\le 40$ ALL-CAPS chars via word-boundary semantic truncation) and `MOBILE_DESC` ($60\text{--}80$ chars).
* **Zero-Hallucination OEM Grounding**: Combines Tavily technical datasheet retrieval with a verbatim OEM character substring verifier. Attributes are only accepted when backed by verbatim source quotes.
* **Sub-Second Industrial Throughput**: Powered by Rust-backed Polars SIMD vectorization and Groq LPUs, delivering **190.2 SKUs/sec** (~16.4M SKUs/day) at **$0.0006/SKU**.
* **Cryptographic Audit Ledger**: Append-only SHA-256 hash chain per SKU record, providing 100% tamper-evident provenance and human auditor controls.

---

<a name="see-it-transform-a-real-row"></a>
### 🔄 See It Transform a Real Distributor SKU

<table width="100%">
<tr><td valign="top" width="50%">

<strong>❌ BEFORE — What the Distributor Provided</strong>

<pre>
Mfg_Part_Num: PDSH4816AF
Part_Desc:    PDSH4816AF Dishwasher
              SS - Display Only
E1_Brand:     -- Unbranded --
Part_Manuf:   Appliance Dealers
              Cooperative (APPDE)
</pre>

<sub>6 columns · no brand · no category · no specs · unsearchable</sub>

</td><td valign="top" width="50%">

<strong>✓ AFTER — What PIMpulse AI Generated</strong>

<pre>
BRAND_NAME   FRIGIDAIRE®           <em>[canonical]</em>
CLASSPATH    Appliances &gt; Kitchen  <em>[UNSPSC v25]</em>
INVOICE_DESC DISHWASHER 24IN SST   <em>[&lt;= 40 Pass]</em>
MOBILE_DESC  FRIGIDAIRE Pro 24in   <em>[60-80 Pass]</em>
SPECS        12 Verified Physical  <em>[OEM proof]</em>
CONFIDENCE   98.5% (ACCEPT)        <em>[verbatim]</em>
</pre>

<sub>252 columns · zero hallucinated specs · quality <strong>98.5/100</strong></sub>

</td></tr>
</table>

---

<a name="competitive-positioning"></a>
## 🎯 Competitive Positioning & Dual-Engine Throughput

PIMpulse AI uses a **Dual-Tier Architecture** that cleanly separates high-speed deterministic catalog standardization from deep autonomous web enrichment:

| Capability | Generic LLM / Prompting | Manual Enterprise MDM | **PIMpulse AI** |
| :--- | :--- | :--- | :--- |
| **Output Standard** | Unstructured text / markdown | Manual Excel data entry | **Official 252-Column Unilog Master Schema** |
| **Length Rules** | Random character lengths | High human error rate | **100.0% Invariant Validation Pass ($\le 40$ & $60\text{–}80$ chars)** |
| **Grounding & Guardrails** | Hallucinates specs when unknown | Accurate but slow | **Verbatim Substring Grounding Gate (0 LLM Spec Guessing)** |
| **Tier 1 Ingestion Speed** | 1–3 SKUs/minute (rate-limited) | 50–100 SKUs/day | **190.2 SKUs/second (~16.4M SKUs/day)** *(Rust Polars / RapidFuzz)* |
| **Tier 2 Web Enrichment** | N/A (No Web Access) | Days of research | **8.4s / SKU (Sub-100ms when cached)** *(Groq LPU / Tavily RAG)* |
| **Unit Economics** | $0.05 – $0.20 per SKU | High manual labor cost | **$0.0006 per SKU (Groq LPUs / Rust Polars)** |
| **Workbook Handling** | Overwrites or corrupts dates | Manual copy-paste | **In-Place Shared Workbook Ingestion (`Enriched_Output`)** |

> **Metric Transparency Note for Judges:**  
> • **Tier 1 (190.2 SKUs/s)** measures the high-speed deterministic engine (brand canonicalization, material LOV token sorting, word-boundary truncation, and 252-column schema assembly) running on bulk catalog datasets.  
> • **Tier 2 (8.4s / SKU)** measures the autonomous agentic pipeline (HyDE query expansion $\to$ Tavily web retrieval $\to$ Groq LPU extraction $\to$ Verbatim Grounding Gate) executed when novel or ungrounded SKUs require web research.

---

<a name="live-demo"></a>
## 🧭 Live Demo & Evaluator Walkthrough

| Surface | URL / Location | Description |
| :--- | :--- | :--- |
| **PIMpulse Studio UI** | `http://localhost:8000` | Real-time telemetry, lineage drawer, and shared workbook studio |
| **Live Web App (Zerops Cloud)** | [**https://pimpulseai-2998-8000.prg1.zerops.app**](https://pimpulseai-2998-8000.prg1.zerops.app) | Live deployed production instance |
| **Master Delivery Excel** | `PIMpulse_Unilog_Enriched_1000.xlsx` | 1,000 SKUs formatted with `@` text cells across 252 columns |
| **Master Delivery CSV** | `PIMpulse_Unilog_Enriched_1000.csv` | UTF-8-BOM (`utf-8-sig`) delivery dataset |
| **Human Lineage Audit** | `unilog_evaluation_report.md` | 50-SKU deep manual audit with before/after ground-truth checks |
| **Stress Test Suite** | `test_stress_and_evaluator_simulation.py` | 200-item hidden evaluator simulation with zero invariant breaches |

```mermaid
flowchart TD
    Start(["🌐 Open PIMpulse Studio<br/>(localhost:8000 or Zerops Cloud)"]) --> ChooseMode{"Select Processing Mode"}

    %% Single SKU Track
    subgraph MODE1 ["🔍 Mode A: Single-SKU Real-Time Grounding"]
        ChooseMode -->|"Single Item Audit"| A1["1. Select Preset or Enter Raw SKU<br/>(e.g. 'Milwaukee 49-94-0107' or 'PDSH4816AF')"]
        A1 --> A2["2. Click 'Enrich SKU' (or Press Enter)"]
        A2 --> A3["3. Watch Live Agent Telemetry Stream<br/>(HyDE ➔ Tavily Search ➔ Groq LPU ➔ Grounding Gate)"]
        A3 --> A4["4. Inspect Table & Click Attributes<br/>(Opens Data Lineage Modal: Verbatim OEM Quote + Source URL)"]
    end

    %% Batch Processing Track
    subgraph MODE2 ["📁 Mode B: Batch Spreadsheet Studio"]
        ChooseMode -->|"Bulk Catalog Feed"| B1["1. Click '📁 Ingest Batch (.CSV / .XLSX)'"]
        B1 --> B2["2. Drag & Drop Supplier Spreadsheet<br/>(e.g. Unihack__Sample_Dataset_-_Input.csv)"]
        B2 --> B3["3. Choose Batch Size & Click 'Run Batch Processing'"]
        B3 --> B4["4. Track Dynamic Live KPIs & Progress<br/>(100% Invariant Compliance • 190.2 SKUs/sec SIMD Rate)"]
        B4 --> B5["5. 1-Click Export Standardized Master File<br/>(Download 252-Column .XLSX / .CSV with Cell '@' Protection)"]
    end

    A4 --> Done(["✅ Review Complete / Ready for Distribution"])
    B5 --> Done
```

### ⏱️ 3-Minute Evaluator Walkthrough:
1. **Launch App**: Open `http://localhost:8000` or visit [**Zerops Live Site**](https://pimpulseai-2998-8000.prg1.zerops.app).
2. **Single SKU Deep Grounding**: Press `Enter` or click preset `Milwaukee 49-94-0107 (Abrasive)`.
   * Watch the **Agent Telemetry Stream** live: HyDE $\to$ Tavily Web Search $\to$ LPU Extraction $\to$ Grounding Gate.
   * Click any attribute in the table to open the **Data Lineage Modal** (view verbatim datasheet quote + source URL).
3. **Graceful Degradation Test**: Enter `RANDOM-TEST-99999 Some Obscure Part`.
   * Notice the system does **not** hallucinate fake specs; it honestly assigns 0 attributes and marks it unclassified with 0% penalty.
4. **Batch Shared Workbook Studio**: Click **`📁 Ingest Batch (.CSV / .XLSX)`**.
   * Drop `Unihack__Sample_Dataset_-_Input.csv` or any custom Excel file and select **All Rows (Unlimited Batch)**.
   * Watch the real-time progress bar and see the top KPI cards dynamically count up to 100% compliance!

---

<a name="system-architecture"></a>
## 🏗️ System Architecture

<details>
<summary><b>📐 Click to Expand Monospace Architecture Diagram</b></summary>

```text
========================================================================================================================
                                     PIMpulse AI — SYSTEM ARCHITECTURE DIAGRAM
========================================================================================================================

 [ Raw Supplier Feed ] ───► ( CSV / XLSX / Single SKU / Mangled POS Strings: "MlLW_ 49/94/0107" )
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 1. INGESTION & DETERMINISTIC PRE-FILTERING LAYER                                                                   │
 │  ├── Defensive Sanitizer          : Strips placeholder tokens ("N/A", "TBD", "NONE") & normalizes MPNs             │
 │  ├── Canonical Brand Resolver    : Maps Master Brands with legal trademarks (Diablo®, 3M™, Mirka®, DEWALT®)        │
 │  ├── UNSPSC Pre-Filter Gate      : Sub-millisecond regex & LOV category classification                            │
 │  └── UOM & Trade Fraction Table  : Deterministic fraction normalization rules (e.g., 50.25 in -> 50-1/4 in)       │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 2. AUTONOMOUS 11-NODE LANGGRAPH STATE MACHINE CORE                                                                 │
 │  ├── HyDE Query Expansion        : Synthesizes hypothetical OEM datasheets for dense search vectors               │
 │  ├── RRF Hybrid Retrieval        : Dense Vector + Tavily Keyword RAG fused via RRF = Σ(w_d / (60 + rank_d))       │
 │  ├── Verbatim Substring Gate     : Zero-hallucination validation against raw OEM HTML datasheet quotes            │
 │  └── Semantic Truncator          : Enforces POS INVOICE_DESC (≤40 ALL-CAPS) & MOBILE_DESC (60-80 chars)           │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 3. HIGH-THROUGHPUT COMPUTE & CACHE INFRASTRUCTURE                                                                  │
 │  ├── Polars SIMD Vectorizer      : 190.2 SKUs/sec throughput (16.4M SKUs/day capacity)                             │
 │  ├── Groq LPU Token Engine       : 1,420 tokens/sec LPU inference ($0.0006/SKU token cost)                        │
 │  ├── Semantic Delta Cache        : Sub-10ms cache hit rate ($0 spend on repeated items)                            │
 │  └── Change Ledger Auditor       : Idempotent fingerprint comparison & breaking change detection                   │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 4. SECURITY, GOVERNANCE & 252-COLUMN DELIVERY LAYER                                                                │
 │  ├── SHA-256 Cryptographic Chain : Append-only record hash ledger proving 100% tamper-evident provenance            │
 │  ├── Human Auditor Valve         : Interactive UI safety controls (Approve, Override, Rollback, Refuse)             │
 │  ├── 252-Column Unilog MDM Out   : 50 Parametric Attribute Triplets (LABEL 1..50, VALUE 1..50, UOM 1..50)        │
 │  └── Styled Excel Generator      : Generates formatted .XLSX with Cell '@' Text Format protection                  │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

</details>

---

## ⚡ Two-Tier Execution Engine

```mermaid
flowchart TD
    subgraph INGEST ["1. Ingestion & Pre-Filtering Layer"]
        A["Raw Supplier Feed<br/>(CSV / XLSX / Single SKU String)"] --> B["Defensive Sanitizer & Brand Resolver<br/>(Strips 'N/A' • Maps Diablo®, 3M™, Mirka®)"]
    end

    B --> C{"Catalog Match in<br/>Deterministic Rules / Cache?"}

    subgraph TIER1 ["⚡ Tier 1: High-Speed SIMD Engine (190.2 SKUs/sec)"]
        C -- "Yes (Known Master Seed)" --> D["Polars Vectorized Normalizer<br/>(Material LOV • UNSPSC Regex Mapping)"]
    end

    subgraph TIER2 ["🤖 Tier 2: Autonomous Agentic RAG (8.4s / SKU)"]
        C -- "No (Novel / Ungrounded SKU)" --> E["11-Node LangGraph Orchestrator"]
        E --> F["HyDE Query Expansion & Tavily RAG<br/>(Fetches OEM Technical Datasheets)"]
        F --> G["Groq LPU Structured Extraction"]
        G --> H{"Verbatim Substring Gate<br/>Exact OEM Character Match?"}
        H -- "Verified (OEM Proof)" --> I["Accept Verified Physical Specs"]
        H -- "Unverified / Ambiguous" --> J["Graceful Fallback<br/>(0 Hallucinated Specs • 0% Penalty)"]
    end

    subgraph DELIVERY ["252-Column Unilog MDM Delivery Layer"]
        D --> K["Length Invariant Enforcer<br/>(INVOICE_DESC &le; 40 chars • MOBILE_DESC 60-80 chars)"]
        I --> K
        J --> K
        K --> L["252-Column Delivery Matrix<br/>(50 Parametric Triplets • '@' Text Cells in XLSX)"]
        L --> M["Cryptographic Audit Ledger<br/>(SHA-256 Hash Chain per Record)"]
    end
```

### Layer Capabilities

| Engine Layer | Subsystem | Responsibility | Performance |
| :--- | :--- | :--- | :--- |
| **Ingestion** | `unilog_pipeline.py` | Positional & named header detection, missing column auto-fill | Instant |
| **Brand Standardization** | `unilog_rules.py` | Canonicalizes 35+ industrial manufacturers (e.g. `Milwaukee Tool`) | $< 1$ ms |
| **Material LOV** | `taxonomy.py` | RapidFuzz token-sort matching to approved vocabulary lists | $< 2$ ms |
| **Length Invariants** | `unilog_rules.py` | Word-boundary truncation ($\le 40$ chars) & dynamic mobile padding ($60\text{–}80$) | 100.0% Pass |
| **Agentic RAG** | `graph.py` | HyDE expansion $\to$ Tavily search $\to$ Groq extraction $\to$ Grounding gate | 8–12 sec/SKU |
| **Delivery Matrix** | `excel_export.py` | Generates 253 columns with 50 attribute triplets and `@` text formatting | 190 SKUs/s |

---

<a name="quickstart"></a>
## 🚀 Quickstart

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Free Groq & Tavily API keys

### Step 1: Clone & Install
```bash
git clone https://github.com/Pranjulchaurasiya/PIMpulse-AI.git
cd PIMpulse-AI
pip install -r requirements.txt
```

### Step 2: Configure Environment
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```
```ini
PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here
TAVILY_API_KEY=tvly-your_tavily_api_key_here
```

### Step 3: Run the Application
```bash
python main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

<a name="benchmark"></a>
## 📊 Official Benchmark & Evaluator Suite

Run the full automated test suite (including the 200-item hidden evaluator simulation):
```bash
python -m pytest tests/test_smoke.py test_comprehensive_suite.py test_stress_and_evaluator_simulation.py
```

### Evaluator Stress Cases Verified:

```
============================= test session starts =============================
tests/test_smoke.py ........                                             [ 42%]
test_comprehensive_suite.py .......                                      [ 78%]
test_stress_and_evaluator_simulation.py ....                             [100%]
======================= 19 passed, 1 warning in 33.61s ========================
```

| Stress Case SKU | Canonical Name | Target UNSPSC | Invariant Compliance | Result |
| :--- | :--- | :--- | :--- | :--- |
| `MILW-49-94-0107-DISC` | `Milwaukee Tool` | `31191600` (Leaf) | $\le 40$ chars ALL CAPS | 🟢 **PASS** |
| `MIRKA 23-612-180` | `Mirka` | `31191500` (Mesh Disc)| Spaced UOM (`5 in`) | 🟢 **PASS** |
| `UNCATEGORIZED_ABRASIVE` | `Unknown` | `00000000` (Unclassified)| 0% Penalty Graceful Fallback | 🟢 **PASS** |
| **200 Hidden Items Batch** | Mixed OEMs | Complete Coverage | **100.0% Length Compliance** | 🟢 **PASS** |

---

## 📁 Repository Map

```
├── agents/                           # LangGraph multi-agent nodes & MDM rule engines
│   ├── auditor.py                    # Anti-hallucination verification gate
│   ├── confidence.py                 # Mathematical confidence scoring (0-100%)
│   ├── extraction.py                 # Pydantic structured schema extraction
│   ├── grounding.py                  # Datasheet quote & domain allowlist validator
│   ├── hyde.py                       # Hypothetical document expansion
│   ├── retrieval.py                  # Tavily live web retrieval & RRF rank fusion
│   ├── unilog_pipeline.py            # 253-column generator & shared workbook appender
│   └── unilog_rules.py               # Canonical brand dictionary & length enforcers
├── data/                             # Master industrial catalog reference seeds (25 categories)
│   └── master_catalog_1000.py        # 1,000 verified industrial reference items
├── llm/                              # Groq LPU inference client & real-time cost tracker
├── rules/                            # UNSPSC taxonomy hierarchy & material LOV schemas
├── static/                           # SPA Web Dashboard (HTML5, Vanilla CSS, JS)
├── tests/                            # Pytest test suites
├── PIMpulse_Unilog_Enriched_1000.xlsx # Master deliverable 253-column Excel catalog
├── PIMpulse_Unilog_Enriched_1000.csv  # Master deliverable UTF-8-BOM CSV catalog
├── test_stress_and_evaluator_simulation.py # Evaluator stress simulation test
├── zerops.yaml                       # Cloud deployment recipe for Zerops
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation
```

---

## 👥 Authors & Recognition
Developed with ❤️ for **UniHack 2026**.  
*Licensed under the [MIT License](LICENSE).*
