# 🎙️ Official Voice Recording Script for Remotion Video
**Target Duration**: Exactly 3 Minutes (180 Seconds) @ 30 FPS  
**Synced File**: `remotion_demo/PIMpulseDemoVideo.tsx`

---

### 🟢 SCENE 1: Introduction & Enterprise Problem (0:00 – 0:30)
**[Frames 0 to 900 in Remotion]**  
*Tone: Professional, authoritative, and energetic.*

> *"In enterprise e-commerce and MRO distribution, onboarding supplier product catalogs takes weeks of manual labor. Vendor data is noisy, descriptions breach character limits in ERP systems, and standard LLMs hallucinate physical specifications when data is missing.*  
> *Meet **PIMpulse AI** — an autonomous, dual-tier product enrichment engine built for UniHack 2026 that standardizes raw supplier data into official 252-column Unilog delivery catalogs with zero LLM spec guessing."*

---

### 🔵 SCENE 2: Single-SKU Agentic Enrichment & Provenance (0:30 – 1:30)
**[Frames 900 to 2700 in Remotion]**  
*Tone: Clear, deliberate, highlighting technical depth.*

> *"When a novel or messy part number enters the pipeline, our 26-node LangGraph autonomous agent kicks in.*  
> *First, it performs HyDE query expansion to predict technical datasheet terminology. Next, it queries Tavily web search, filtering out consumer e-commerce marketplaces to retrieve verbatim manufacturer datasheets. Groq LPUs extract structured attributes in milliseconds, and our **Verbatim Substring Grounding Gate** validates every extracted value against exact datasheet quotes before confirming it.*  
> *Every attribute links to a complete data lineage modal showing the source URL and exact verbatim quote."*

---

### 🟣 SCENE 3: Deterministic Invariant Enforcement & Fallback (1:30 – 2:15)
**[Frames 2700 to 4050 in Remotion]**  
*Tone: Confident, demonstrating enterprise safety.*

> *"PIMpulse AI mathematically guarantees Unilog length rules: `INVOICE_DESC` is strictly formatted under 40 characters using word-boundary truncation in ALL CAPS, while `MOBILE_DESC` is dynamically padded to between 60 and 80 characters with a 100% pass rate.*  
> *Crucially, if an obscure or invalid part like `RANDOM-TEST-99999` is processed, our system refuses to hallucinate fake specs. It gracefully marks the item as unclassified with zero penalty — engineered for production reliability."*

---

### 🟡 SCENE 4: Batch Shared Workbook Studio & Delivery (2:15 – 3:00)
**[Frames 4050 to 5400 in Remotion]**  
*Tone: High-energy closing, decisive.*

> *"For bulk operations, our Tier 1 Rust Polars Engine standardizes input spreadsheets at 190 SKUs per second.*  
> *Users simply drag and drop raw CSV or Excel workbooks into our Shared Workbook Studio. The engine cleans placeholders, enforces all 252 delivery columns, and appends the `Enriched_Output` sheet in-place without corrupting date cells.*  
> *Judges can inspect all 1,002 enriched records live in the Master Catalog Studio tab or export the complete 252-column Excel deliverable with one click.*  
> *PIMpulse AI: Fast, grounded, and 100% compliant. Thank you!"*

---

### 🎙️ Recording Tips for Best Audio Sync:
1. Speak at a steady, natural pace (~130 words per minute).
2. Take a brief 1-second pause between scenes at **0:30**, **1:30**, and **2:15**.
3. Export your final recording as **`voiceover.mp3`** and place it into `remotion_demo/public/voiceover.mp3`.
