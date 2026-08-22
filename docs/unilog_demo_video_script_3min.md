# 🎬 PIMpulse AI — 3-Minute Official Demo Video Script (UniHack 2026 / Unilog Track)

> **Tone**: Clear, direct, professional engineer. Plain English, zero fluff or AI buzzwords.  
> **Total Duration**: 3:00 (180 Seconds)  
> **Key Focus Points**: Unilog 252-column delivery standard, 40-character POS invoice limit, verbatim OEM grounding, multi-tab Excel workbook preservation.

---

## ⏱️ Timeline & Scene Breakdown

### 📍 Scene 1: The B2B Catalog Problem (0:00 – 0:30)
**Visual**: Show messy raw supplier CSV/XLSX file with mangled names like `MlLW_ 49/94/0107 (4031) !!` and truncated descriptions.

* **Voiceover**:  
  "Industrial distributors process millions of raw product feeds every day. But supplier data is usually dirty, abbreviated, and incomplete.  
  Standard LLMs try to fix this by guessing, but in B2B commerce, a hallucinated thread size or voltage breaks order fulfillment.  
  Even worse, delivery standards like Unilog require strict length rules—like an invoice description capped at 40 characters—and exact 252-column spreadsheet structures.  
  This is why we built **PIMpulse AI**: an automated catalog engine designed specifically for industrial product data."

---

### 📍 Scene 2: Live Enrichment & Grounding Proof (0:30 – 1:15)
**Visual**: Open PIMpulse AI web dashboard at `https://pimpulseai-2998-8000.prg1.zerops.app/`. Click the sample query `PDSH4816AF (Frigidaire Dishwasher)` and click **Enrich Profile**.

* **Voiceover**:  
  "Let's see how it works in real time.  
  Here, we input a raw part number: `PDSH4816AF`.  
  In under two seconds, the engine identifies the brand, classifies the product under UNSPSC taxonomy code `52141501`, and extracts verified physical attributes like voltage, sound level, and dimensions.  
  Notice the **Verbatim Grounding Status**: every single extracted attribute links directly to exact text inside official manufacturer datasheets. If a detail cannot be proven from real OEM documentation, the system refuses to guess."

---

### 📍 Scene 3: Unilog Length Invariants & Excel Standard (1:15 – 1:55)
**Visual**: Zoom into the **POS INVOICE_DESC Length Meter** (`PDSH4816AF DISHWASHER 24IN SS` — 32 / 40 chars) and click **Download (.XLSX)**.

* **Voiceover**:  
  "Now look at the strict delivery standards.  
  For `INVOICE_DESC`, ERP point-of-sale systems reject any string longer than 40 characters. PIMpulse AI automatically formats the title into clean, uppercase short text without cutting off critical words.  
  For e-commerce catalogs, it builds a full 60 to 80 character description.  
  When you export, PIMpulse AI formats all 252 Unilog columns—including primary specs, unit of measure fields, and asset links—ready for immediate database upload."

---

### 📍 Scene 4: Shared Workbook Batch Processing & Speed (1:55 – 2:30)
**Visual**: Click **Ingest Batch (.CSV / .XLSX)**, drag and drop a 1,000-row catalog file, and show real-time Polars SIMD speed (190 SKUs/sec).

* **Voiceover**:  
  "For enterprise catalogs, you don't process items one by one.  
  You can drag and drop an entire raw supplier workbook.  
  Powered by a high-speed Rust Polars data pipeline, PIMpulse AI processes over 190 items per second.  
  Instead of breaking your original file format, it preserves all existing sheets and appends a standardized `Enriched_Output` tab directly into your workbook, preserving all formulas and formatting."

---

### 📍 Scene 5: Human Auditor Governance & Conclusion (2:30 – 3:00)
**Visual**: Show the **Auditor Governance Card** with options `Approve & Publish`, `Manual Override`, `Rollback Snapshot`, `Refuse Row`. Show final score 100% Pass Rate.

* **Voiceover**:  
  "Finally, data quality requires human control.  
  If a record falls below a 70% confidence threshold, it triggers our Auditor Governance valve. Catalog managers can review exact source lineage, override values, or rollback changes using SHA-256 cryptographic audit hashes.  
  PIMpulse AI turns raw, messy vendor files into 100% compliant, verified Unilog master catalogs at high speed.  
  Thank you."

---

## 🎯 Recording Tips for Presenters

1. **Keep your voice steady and natural** — speak like you are giving a live technical demo to a senior software engineer at Unilog.
2. **Cursor movement**: Keep mouse movements calm and deliberate. Pause for 1 second on key cards (Invoice Length Meter, Verbatim Proof table) so judges can read the numbers clearly.
3. **Screen resolution**: Record at 1080p (1920x1080) with browser zoom at 100%.
