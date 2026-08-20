# 🎬 Remotion Video Generator Guide for PIMpulse AI

This standalone Remotion suite renders a 100% frame-accurate, high-definition (1920x1080 @ 30fps) pitch video of **PIMpulse AI** synced frame-by-frame to your voiceover recording without touching any existing project backend files.

---

## 🚀 Quickstart in 3 Steps

### Step 1: Add Your Voiceover Audio File
Save your voiceover audio recording as **`voiceover.mp3`** inside the public folder:
```
remotion_demo/
  └── public/
        └── voiceover.mp3   <-- Drop your audio recording file here!
```

---

### Step 2: Preview the Video Studio Live
Run the interactive Remotion Studio to preview the video and verify audio sync in your browser:

```bash
npx remotion studio remotion_demo/PIMpulseDemoVideo.tsx
```

---

### Step 3: Render the Final Production MP4 Video
Render the full 3-minute 1080p MP4 video with a single command:

```bash
npx remotion render remotion_demo/PIMpulseDemoVideo.tsx PIMpulseDemoVideo.mp4
```

---

## 📂 Scene Timeline Breakdown

| Scene | Timestamp | Frame Range | Visual Focus |
| :--- | :--- | :--- | :--- |
| **Scene 1: Intro & Problem** | 0:00 – 0:30 | 0 – 900 | Glassmorphic Brand Hero, UniHack Badge, Problem vs Solution |
| **Scene 2: Agentic Enrichment** | 0:30 – 1:30 | 900 – 2700 | Single SKU Search, 26-Node Telemetry, Grounding Substring Gate |
| **Scene 3: Invariant Rules** | 1:30 – 2:15 | 2700 – 4050 | `INVOICE_DESC` (&le;40 chars) & `MOBILE_DESC` (60–80 chars) compliance |
| **Scene 4: Shared Workbook** | 2:15 – 3:00 | 4050 – 5400 | Batch Ingestion Studio, 190 SKUs/s Throughput, XLSX Download |

---

## 💡 Customization & Fine-Tuning

- **Adjust Video Duration**: If your audio file is longer or shorter than 3 minutes, update `durationInFrames` in [`remotion_demo/PIMpulseDemoVideo.tsx`](file:///c:/Users/pranj/Documents/PIMpulse%20AI/remotion_demo/PIMpulseDemoVideo.tsx).
- **Zero File Changes**: This suite is stored isolated in `remotion_demo/` — your core application files in `main.py`, `graph.py`, and `static/index.html` remain 100% untouched.
