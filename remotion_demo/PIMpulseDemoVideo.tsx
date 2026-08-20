import { Composition, Folder, staticFile, Audio, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import React from "react";

// ============================================================================
// PIMpulse AI — UniHack 2026 Demo Video Remotion Suite
// Frame-accurate React Video Composition synced to Voiceover Audio
// ============================================================================

const FPS = 30;
const DURATION_IN_FRAMES = 180 * FPS; // 3 Minutes (5400 frames) @ 30fps

// Color Tokens matching PIMpulse Glassmorphic Theme
const COLORS = {
  bgBase: "#06090e",
  bgSurface: "#0c1017",
  bgCard: "#121824",
  borderSubtle: "#1e293b",
  borderBright: "#334155",
  accentCyan: "#38bdf8",
  accentEmerald: "#10b981",
  accentViolet: "#8b5cf6",
  accentAmber: "#f59e0b",
  textMain: "#f8fafc",
  textMuted: "#94a3b8",
  textDim: "#64748b",
};

// ----------------------------------------------------------------------------
// Scene 1: Title & Enterprise Problem Intro (0:00 - 0:30 | 0 to 900 frames)
// ----------------------------------------------------------------------------
const TitleScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const titleScale = spring({ frame, fps, config: { damping: 12 } });

  const problemSlideUp = interpolate(frame, [150, 190], [50, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const problemOpacity = interpolate(frame, [150, 190], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: COLORS.bgBase,
        color: COLORS.textMain,
        fontFamily: "Inter, sans-serif",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Background Radial Glow */}
      <div
        style={{
          position: "absolute",
          width: "800px",
          height: "800px",
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, rgba(139, 92, 246, 0.05) 50%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />

      {/* Brand Hero Badge */}
      <div
        style={{
          opacity: titleOpacity,
          transform: `scale(${titleScale})`,
          display: "flex",
          alignItems: "center",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        <div
          style={{
            width: "64px",
            height: "64px",
            borderRadius: "16px",
            background: "linear-gradient(135deg, #0284c7, #8b5cf6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "32px",
            boxShadow: "0 0 30px rgba(56, 189, 248, 0.4)",
          }}
        >
          ⚡
        </div>
        <div>
          <h1 style={{ fontSize: "54px", fontWeight: 800, margin: 0, letterSpacing: "-0.03em" }}>
            PIMpulse AI
          </h1>
          <span
            style={{
              fontSize: "14px",
              fontWeight: 700,
              color: COLORS.accentCyan,
              textTransform: "uppercase",
              letterSpacing: "0.15em",
            }}
          >
            UniHack 2026 Submission
          </span>
        </div>
      </div>

      <h2
        style={{
          opacity: titleOpacity,
          fontSize: "26px",
          fontWeight: 500,
          color: COLORS.textMuted,
          textAlign: "center",
          maxWidth: "900px",
          lineHeight: 1.4,
          marginBottom: "50px",
        }}
      >
        Autonomous Enterprise Product Enrichment &amp; MDM Delivery Engine
      </h2>

      {/* Problem vs Solution Card Grid */}
      <div
        style={{
          opacity: problemOpacity,
          transform: `translateY(${problemSlideUp}px)`,
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "24px",
          width: "100%",
          maxWidth: "1100px",
        }}
      >
        {/* Traditional Problem Card */}
        <div
          style={{
            backgroundColor: COLORS.bgCard,
            border: `1px solid ${COLORS.borderSubtle}`,
            borderRadius: "16px",
            padding: "32px",
            boxShadow: "0 10px 30px rgba(0,0,0,0.5)",
          }}
        >
          <div style={{ color: "#f43f5e", fontSize: "16px", fontWeight: 700, marginBottom: "12px" }}>
            ❌ TRADITIONAL MDM BOTTLENECK
          </div>
          <ul style={{ color: COLORS.textMuted, fontSize: "15px", lineHeight: 1.8, paddingLeft: "20px", margin: 0 }}>
            <li>Weeks of manual catalog data entry</li>
            <li>Random character limit breaches in ERP</li>
            <li>Generic LLMs hallucinating physical specs</li>
            <li>Missing verbatim datasheet provenance</li>
          </ul>
        </div>

        {/* PIMpulse AI Solution Card */}
        <div
          style={{
            backgroundColor: COLORS.bgCard,
            border: `1px solid ${COLORS.accentCyan}`,
            borderRadius: "16px",
            padding: "32px",
            boxShadow: "0 0 30px rgba(56, 189, 248, 0.15)",
          }}
        >
          <div style={{ color: COLORS.accentEmerald, fontSize: "16px", fontWeight: 700, marginBottom: "12px" }}>
            ⚡ PIMpulse AI SOLUTION
          </div>
          <ul style={{ color: COLORS.textMain, fontSize: "15px", lineHeight: 1.8, paddingLeft: "20px", margin: 0 }}>
            <li><strong>190 SKUs/sec</strong> Tier 1 Bulk Standardization</li>
            <li><strong>252-Column</strong> Official Unilog Delivery Schema</li>
            <li><strong>Verbatim Substring Gate</strong> (0 LLM Spec Guessing)</li>
            <li><strong>100% Invariant Pass Rate</strong> (&le;40 &amp; 60–80 chars)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------------------
// Scene 2: Single SKU Deep Grounding & Telemetry (0:30 - 1:30 | 900 to 2700 frames)
// ----------------------------------------------------------------------------
const SingleSkuScene: React.FC = () => {
  const frame = useCurrentFrame();

  const activeNode = Math.min(6, Math.floor((frame - 900) / 250) + 1);

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: COLORS.bgBase,
        color: COLORS.textMain,
        fontFamily: "Inter, sans-serif",
        padding: "40px",
        display: "grid",
        gridTemplateColumns: "380px 1fr",
        gap: "24px",
      }}
    >
      {/* Telemetry Stream Left Sidebar */}
      <div
        style={{
          backgroundColor: COLORS.bgSurface,
          border: `1px solid ${COLORS.borderSubtle}`,
          borderRadius: "16px",
          padding: "24px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
        }}
      >
        <div style={{ fontSize: "14px", fontWeight: 700, color: COLORS.accentCyan, display: "flex", justifyContent: "space-between" }}>
          <span>📡 LangGraph Telemetry Stream</span>
          <span>{activeNode}/6 Nodes</span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {[
            "1. Taxonomy Pre-Filter (UNSPSC 31191600)",
            "2. HyDE Speculative Expansion",
            "3. Tavily Live Web Search (OEM Filter)",
            "4. Groq LPU Attribute Extraction",
            "5. Grounding Substring Gate",
            "6. Invariant Validation (100% Pass)",
          ].map((nodeName, idx) => (
            <div
              key={idx}
              style={{
                backgroundColor: idx + 1 <= activeNode ? COLORS.bgCard : "transparent",
                border: `1px solid ${idx + 1 <= activeNode ? COLORS.accentCyan : COLORS.borderSubtle}`,
                borderRadius: "10px",
                padding: "12px",
                fontSize: "13px",
                color: idx + 1 <= activeNode ? COLORS.textMain : COLORS.textDim,
                transition: "all 0.3s",
              }}
            >
              {nodeName} {idx + 1 <= activeNode ? "✓" : ""}
            </div>
          ))}
        </div>
      </div>

      {/* Main Single SKU Output Card */}
      <div
        style={{
          backgroundColor: COLORS.bgCard,
          border: `1px solid ${COLORS.borderBright}`,
          borderRadius: "16px",
          padding: "32px",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <span style={{ fontSize: "12px", color: COLORS.accentCyan, fontWeight: 700 }}>UNSPSC 31191600 &gt; Abrasives &gt; Cut-off Wheels</span>
            <h2 style={{ fontSize: "28px", fontWeight: 800, margin: "4px 0" }}>Milwaukee 49-94-0107</h2>
            <div style={{ fontSize: "14px", color: COLORS.textMuted }}>3" x 1/16" x 3/8" Cut-off Wheel (10,000 RPM)</div>
          </div>
          <div
            style={{
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              border: `1px solid ${COLORS.accentEmerald}`,
              color: COLORS.accentEmerald,
              padding: "8px 16px",
              borderRadius: "20px",
              fontSize: "14px",
              fontWeight: 800,
            }}
          >
            ACCEPT (94.2% Confidence)
          </div>
        </div>

        {/* Verbatim Physical Attributes Table */}
        <div style={{ backgroundColor: COLORS.bgSurface, borderRadius: "12px", padding: "16px", border: `1px solid ${COLORS.borderSubtle}` }}>
          <div style={{ fontSize: "13px", fontWeight: 700, color: COLORS.accentCyan, marginBottom: "12px" }}>
            Verified Parametric Attributes (Grounding Gate Verified)
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ color: COLORS.textMuted, textAlign: "left" }}>
                <th style={{ padding: "8px" }}>Attribute Label</th>
                <th style={{ padding: "8px" }}>Verified Value</th>
                <th style={{ padding: "8px" }}>UOM</th>
                <th style={{ padding: "8px" }}>Verbatim Provenance Quote</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderTop: `1px solid ${COLORS.borderSubtle}` }}>
                <td style={{ padding: "8px", fontWeight: 600 }}>Wheel Diameter</td>
                <td style={{ padding: "8px", color: COLORS.accentEmerald, fontWeight: 700 }}>3</td>
                <td style={{ padding: "8px", color: COLORS.textMuted }}>in</td>
                <td style={{ padding: "8px", color: COLORS.textDim, fontStyle: "italic" }}>"3 in. Abrasive Cut-Off Wheel"</td>
              </tr>
              <tr style={{ borderTop: `1px solid ${COLORS.borderSubtle}` }}>
                <td style={{ padding: "8px", fontWeight: 600 }}>Thickness</td>
                <td style={{ padding: "8px", color: COLORS.accentEmerald, fontWeight: 700 }}>1/16</td>
                <td style={{ padding: "8px", color: COLORS.textMuted }}>in</td>
                <td style={{ padding: "8px", color: COLORS.textDim, fontStyle: "italic" }}>"1/16 in. wheel thickness"</td>
              </tr>
              <tr style={{ borderTop: `1px solid ${COLORS.borderSubtle}` }}>
                <td style={{ padding: "8px", fontWeight: 600 }}>Arbor Size</td>
                <td style={{ padding: "8px", color: COLORS.accentEmerald, fontWeight: 700 }}>3/8</td>
                <td style={{ padding: "8px", color: COLORS.textMuted }}>in</td>
                <td style={{ padding: "8px", color: COLORS.textDim, fontStyle: "italic" }}>"3/8 in. arbor hole"</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------------------
// Scene 3: Invariant Length Validation & Graceful Fallback (1:30 - 2:15 | 2700 to 4050 frames)
// ----------------------------------------------------------------------------
const InvariantScene: React.FC = () => {
  return (
    <div
      style={{
        flex: 1,
        backgroundColor: COLORS.bgBase,
        color: COLORS.textMain,
        fontFamily: "Inter, sans-serif",
        padding: "60px",
        display: "flex",
        flexDirection: "column",
        gap: "32px",
        justifyContent: "center",
      }}
    >
      <h2 style={{ fontSize: "36px", fontWeight: 800, textAlign: "center", margin: 0 }}>
        ⚡ Deterministic Invariant Enforcement &amp; Graceful Degradation
      </h2>

      {/* Invariant Rules Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
        {/* INVOICE_DESC Rule */}
        <div style={{ backgroundColor: COLORS.bgCard, border: `1px solid ${COLORS.accentEmerald}`, borderRadius: "16px", padding: "28px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "14px", fontWeight: 700, color: COLORS.accentCyan }}>INVOICE_DESC RULE</span>
            <span style={{ backgroundColor: "rgba(16, 185, 129, 0.2)", color: COLORS.accentEmerald, padding: "4px 10px", borderRadius: "6px", fontSize: "12px", fontWeight: 800 }}>
              &le; 40 Chars (ALL CAPS)
            </span>
          </div>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "16px", color: COLORS.textMain, backgroundColor: COLORS.bgSurface, padding: "14px", borderRadius: "8px", border: `1px solid ${COLORS.borderSubtle}` }}>
            MILW 3X1/16X3/8 CUTOFF WHEEL 10PK
          </div>
          <div style={{ fontSize: "12px", color: COLORS.accentEmerald, marginTop: "8px", fontWeight: 600 }}>✓ 34 / 40 Characters — 100% Pass</div>
        </div>

        {/* MOBILE_DESC Rule */}
        <div style={{ backgroundColor: COLORS.bgCard, border: `1px solid ${COLORS.accentEmerald}`, borderRadius: "16px", padding: "28px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
            <span style={{ fontSize: "14px", fontWeight: 700, color: COLORS.accentCyan }}>MOBILE_DESC RULE</span>
            <span style={{ backgroundColor: "rgba(16, 185, 129, 0.2)", color: COLORS.accentEmerald, padding: "4px 10px", borderRadius: "6px", fontSize: "12px", fontWeight: 800 }}>
              60 – 80 Chars (Full Context)
            </span>
          </div>
          <div style={{ fontFamily: "JetBrains Mono, monospace", fontSize: "14px", color: COLORS.textMain, backgroundColor: COLORS.bgSurface, padding: "14px", borderRadius: "8px", border: `1px solid ${COLORS.borderSubtle}` }}>
            Milwaukee Tool, 3 in x 1/16 in Cut-off Wheel, 49-94-0107, Heavy Duty
          </div>
          <div style={{ fontSize: "12px", color: COLORS.accentEmerald, marginTop: "8px", fontWeight: 600 }}>✓ 68 Chars [Range 60-80] — 100% Pass</div>
        </div>
      </div>

      {/* Honest Degradation Demo Box */}
      <div style={{ backgroundColor: COLORS.bgSurface, border: `1px dashed ${COLORS.accentAmber}`, borderRadius: "16px", padding: "24px", display: "flex", alignItems: "center", gap: "20px" }}>
        <div style={{ fontSize: "36px" }}>🛡️</div>
        <div>
          <div style={{ fontSize: "16px", fontWeight: 700, color: COLORS.accentAmber }}>Zero-Hallucination Degradation Protection</div>
          <div style={{ fontSize: "14px", color: COLORS.textMuted, marginTop: "4px" }}>
            When given garbage input like <code>RANDOM-TEST-99999</code>, PIMpulse AI assigns 0 attributes and marks it <strong>Unclassified (0% Penalty)</strong> rather than hallucinating fake data.
          </div>
        </div>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------------------
// Scene 4: Batch Shared Workbook & Master Catalog Studio (2:15 - 3:00 | 4050 to 5400 frames)
// ----------------------------------------------------------------------------
const BatchStudioScene: React.FC = () => {
  return (
    <div
      style={{
        flex: 1,
        backgroundColor: COLORS.bgBase,
        color: COLORS.textMain,
        fontFamily: "Inter, sans-serif",
        padding: "40px",
        display: "flex",
        flexDirection: "column",
        gap: "24px",
      }}
    >
      {/* Top Banner KPI Scorecard */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px" }}>
        <div style={{ backgroundColor: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}`, padding: "16px", borderRadius: "12px" }}>
          <div style={{ fontSize: "24px", fontWeight: 800, fontFamily: "JetBrains Mono" }}>1,002</div>
          <div style={{ fontSize: "12px", color: COLORS.textMuted }}>ACTIVE CATALOG SKUS</div>
        </div>
        <div style={{ backgroundColor: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}`, padding: "16px", borderRadius: "12px" }}>
          <div style={{ fontSize: "24px", fontWeight: 800, fontFamily: "JetBrains Mono", color: COLORS.accentCyan }}>252</div>
          <div style={{ fontSize: "12px", color: COLORS.textMuted }}>UNILOG DELIVERY COLUMNS</div>
        </div>
        <div style={{ backgroundColor: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}`, padding: "16px", borderRadius: "12px" }}>
          <div style={{ fontSize: "24px", fontWeight: 800, fontFamily: "JetBrains Mono", color: COLORS.accentEmerald }}>100%</div>
          <div style={{ fontSize: "12px", color: COLORS.textMuted }}>INVARIANT PASS RATE</div>
        </div>
        <div style={{ backgroundColor: COLORS.bgCard, border: `1px solid ${COLORS.borderSubtle}`, padding: "16px", borderRadius: "12px" }}>
          <div style={{ fontSize: "24px", fontWeight: 800, fontFamily: "JetBrains Mono", color: COLORS.accentViolet }}>190.2</div>
          <div style={{ fontSize: "12px", color: COLORS.textMuted }}>SKUs / SEC THROUGHPUT</div>
        </div>
      </div>

      {/* Master Catalog Table View */}
      <div style={{ backgroundColor: COLORS.bgCard, border: `1px solid ${COLORS.borderBright}`, borderRadius: "16px", padding: "24px", flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <div style={{ fontSize: "16px", fontWeight: 700, color: COLORS.accentCyan }}>Master Catalog Studio (1,002 Total Enriched Records)</div>
          <div style={{ backgroundColor: COLORS.accentCyan, color: "#000", padding: "8px 16px", borderRadius: "8px", fontSize: "13px", fontWeight: 800 }}>
            📥 Download Master (.XLSX)
          </div>
        </div>

        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ color: COLORS.textMuted, textAlign: "left", borderBottom: `1px solid ${COLORS.borderBright}` }}>
              <th style={{ padding: "12px" }}>MPN</th>
              <th style={{ padding: "12px" }}>Brand</th>
              <th style={{ padding: "12px" }}>Invoice Desc (&le;40 Chars)</th>
              <th style={{ padding: "12px" }}>Mobile Desc (60-80 Chars)</th>
              <th style={{ padding: "12px" }}>UNSPSC</th>
            </tr>
          </thead>
          <tbody>
            {[
              { mpn: "49-94-0107", brand: "Milwaukee", inv: "MILW 3X1/16X3/8 CUTOFF WHEEL 10PK", mob: "Milwaukee Tool, 3 in x 1/16 in Cut-off Wheel, 49-94-0107, Heavy Duty", unspsc: "31191600" },
              { mpn: "DCB518ASTS06G", brand: "Diablo", inv: "DIAB 1/2X1X8 SND BLT", mob: "Freud America, Inc., Sanding Belt, DCB518ASTS06G, 1/2 in x 8 in", unspsc: "31191500" },
              { mpn: "3MABR-7100075678", brand: "3M", inv: "3M P150 DISC", mob: "3M Company, Drill Bit, 3MABR-7100075678, P150 Grit, Industrial", unspsc: "27112800" },
              { mpn: "3RT2015-1BB41", brand: "Siemens", inv: "SIEMENS 3RT2015-1BB41 MOTOR CONTACTOR", mob: "Siemens 3RT2015-1BB41 SIRIUS Motor Contactor 4kW 24VDC 3-Pole", unspsc: "39121529" },
            ].map((r, i) => (
              <tr key={i} style={{ borderBottom: `1px solid ${COLORS.borderSubtle}` }}>
                <td style={{ padding: "12px", fontFamily: "JetBrains Mono", color: COLORS.accentCyan, fontWeight: 700 }}>{r.mpn}</td>
                <td style={{ padding: "12px", fontWeight: 600 }}>{r.brand}</td>
                <td style={{ padding: "12px" }}>{r.inv}</td>
                <td style={{ padding: "12px", color: COLORS.textMuted }}>{r.mob}</td>
                <td style={{ padding: "12px", color: COLORS.accentViolet, fontFamily: "JetBrains Mono" }}>{r.unspsc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ----------------------------------------------------------------------------
// Main Video Master Composition with Voiceover Audio Track
// ----------------------------------------------------------------------------
export const MainVideo: React.FC = () => {
  return (
    <div style={{ flex: 1, backgroundColor: COLORS.bgBase }}>
      {/* Synchronized Voiceover Audio Track */}
      <Audio src={staticFile("voiceover.mp3")} />

      {/* Sequence 1: Problem & Architecture (0:00 - 0:30) */}
      <Sequence from={0} durationInFrames={900}>
        <TitleScene />
      </Sequence>

      {/* Sequence 2: Single SKU Deep Grounding (0:30 - 1:30) */}
      <Sequence from={900} durationInFrames={1800}>
        <SingleSkuScene />
      </Sequence>

      {/* Sequence 3: Invariant Rules & Graceful Fallback (1:30 - 2:15) */}
      <Sequence from={2700} durationInFrames={1350}>
        <InvariantScene />
      </Sequence>

      {/* Sequence 4: Shared Workbook & Batch Studio (2:15 - 3:00) */}
      <Sequence from={4050} durationInFrames={1350}>
        <BatchStudioScene />
      </Sequence>
    </div>
  );
};

// ----------------------------------------------------------------------------
// Remotion Root Declaration
// ----------------------------------------------------------------------------
export const RemotionRoot: React.FC = () => {
  return (
    <Folder name="PIMpulse_AI_Demo">
      <Composition
        id="PIMpulseDemoVideo"
        component={MainVideo}
        durationInFrames={5400} // 3 Minutes
        fps={30}
        width={1920}
        height={1080}
      />
    </Folder>
  );
};

export default RemotionRoot;
