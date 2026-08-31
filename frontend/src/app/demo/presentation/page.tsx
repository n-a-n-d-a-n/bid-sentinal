'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, ChevronLeft, ChevronRight, Monitor, Play, ShieldCheck } from 'lucide-react';

const SLIDES = [
  {
    title: "PROCUREX",
    subtitle: "AI-Powered Integrated Bid Compliance Verification & Governance Platform for GeM Procurement",
    tagline: "Verify. Explain. Detect. Decide.",
    content: (
      <div className="text-center space-y-4">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-blue-600 font-bold text-white text-4xl shadow-xl shadow-blue-900/50">
          P
        </div>
        <p className="text-slate-300 max-w-xl mx-auto">
          An evidence-grounded intelligence platform designed to assist procurement officers in making fast, transparent, and legally auditable procurement decisions.
        </p>
      </div>
    )
  },
  {
    title: "1. The Core Problem",
    subtitle: "Manual Procurement Review Pain Points",
    content: (
      <div className="grid grid-cols-2 gap-4 text-xs">
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 space-y-2">
          <span className="font-bold text-rose-400 font-mono">DOCUMENT INSPECTION OVERHEAD</span>
          <p className="text-slate-300">Procurement officers manually process hundreds of pages of financial statements, technical specifications, and certificates per tender.</p>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 space-y-2">
          <span className="font-bold text-rose-400 font-mono">HIDDEN NETWORK CONCENTRATIONS</span>
          <p className="text-slate-300">Collusive bidding rings share directors, addresses, or bank accounts without detection across fragmented procurement systems.</p>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 space-y-2">
          <span className="font-bold text-rose-400 font-mono">UNVERIFIED CREDENTIALS</span>
          <p className="text-slate-300">Lack of automated real-time verification against GST, MCA, PAN, Udyam, and Debarment registries.</p>
        </div>
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 space-y-2">
          <span className="font-bold text-rose-400 font-mono">POLICY INTERPRETATION DELAYS</span>
          <p className="text-slate-300">Navigating complex GFR 2017 & GeM manual guidelines leads to inconsistent decision grounds.</p>
        </div>
      </div>
    )
  },
  {
    title: "2. The PROCUREX Solution",
    subtitle: "End-to-End Intelligence Pipeline",
    content: (
      <div className="flex flex-col items-center gap-3 font-mono text-xs text-slate-200">
        <div className="flex items-center gap-2 p-3 rounded-lg border border-blue-800 bg-blue-950/60 w-full max-w-xl justify-between">
          <span>1. DOCUMENT INGESTION</span>
          <span className="text-blue-400 font-bold">PyMuPDF + OCR + Magic Bytes</span>
        </div>
        <div className="flex items-center gap-2 p-3 rounded-lg border border-emerald-800 bg-emerald-950/60 w-full max-w-xl justify-between">
          <span>2. REQUIREMENT & EVIDENCE EXTRACTION</span>
          <span className="text-emerald-400 font-bold">17 Canonical Requirement Types</span>
        </div>
        <div className="flex items-center gap-2 p-3 rounded-lg border border-amber-800 bg-amber-950/60 w-full max-w-xl justify-between">
          <span>3. GOVERNMENT VERIFICATION & GRAPH</span>
          <span className="text-amber-400 font-bold">10 Adapters + NetworkX Centrality</span>
        </div>
        <div className="flex items-center gap-2 p-3 rounded-lg border border-purple-800 bg-purple-950/60 w-full max-w-xl justify-between">
          <span>4. OFFICER GOVERNANCE & AUDIT</span>
          <span className="text-purple-400 font-bold">Mandatory Justification + SHA-256 Ledger</span>
        </div>
      </div>
    )
  },
  {
    title: "3. Non-Negotiable Governance Principles",
    subtitle: "AI Assists · Deterministic Rules Evaluate · Humans Decide",
    content: (
      <div className="space-y-3 font-mono text-xs">
        <div className="p-3 rounded border border-rose-900/60 bg-rose-950/30 text-rose-300">
          ✓ UNKNOWN != PASS | UNAVAILABLE != PASS | LOW_CONFIDENCE != PASS | MISSING_DOCUMENT != PASS
        </div>
        <div className="p-3 rounded border border-emerald-900/60 bg-emerald-950/30 text-emerald-300">
          ✓ AI & ML models MUST NOT autonomously make final legal qualification or disqualification decisions.
        </div>
        <div className="p-3 rounded border border-amber-900/60 bg-amber-950/30 text-amber-300">
          ✓ Anomaly scores & graph relationships are advisory signals — neutral terminology enforced throughout UI.
        </div>
        <div className="p-3 rounded border border-blue-900/60 bg-blue-950/30 text-blue-300">
          ✓ System recommendations & officer decisions are explicitly separated. Overrides require written justification.
        </div>
      </div>
    )
  },
  {
    title: "4. Document Intelligence & Provenance",
    subtitle: "100% Traceable Extraction Provenance",
    content: (
      <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/80 text-xs space-y-3">
        <div className="font-mono font-bold text-white">Extracted Turnover Evidence</div>
        <div className="p-3 rounded bg-slate-950 border border-slate-850 font-mono text-emerald-400">
          Field: Annual Financial Turnover | Extracted Value: ₹ 3,20,00,000 INR | Confidence: 97%
        </div>
        <p className="italic text-slate-400">&ldquo;Audited Financial Statement FY2024.pdf (Page 7): Average annual financial turnover during the last 3 financial years is ₹3.2 Crore.&rdquo;</p>
      </div>
    )
  },
  {
    title: "5. Requirement Intelligence Engine",
    subtitle: "17 Canonical Requirement Types Normalized",
    content: (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 space-y-2 font-mono text-xs">
        <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-850">
          <span>FINANCIAL / TURNOVER</span>
          <span className="text-amber-400">&gt;= ₹ 5,00,00,000</span>
          <span className="text-rose-400 font-bold">MANUAL_REVIEW</span>
        </div>
        <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-850">
          <span>TAX / GSTIN</span>
          <span className="text-amber-400">REQUIRED</span>
          <span className="text-emerald-400 font-bold">PASS</span>
        </div>
        <div className="flex justify-between p-2 rounded bg-slate-950 border border-slate-850">
          <span>LEGAL / BLACKLIST</span>
          <span className="text-amber-400">EXISTS</span>
          <span className="text-emerald-400 font-bold">PASS</span>
        </div>
      </div>
    )
  },
  {
    title: "6. Government Verification Center",
    subtitle: "10 Resilience Adapters (Circuit Breakers + Rate Limiters + Cache)",
    content: (
      <div className="grid grid-cols-3 gap-3 font-mono text-xs">
        <div className="p-3 rounded bg-slate-900 border border-slate-800 text-center">
          <span className="block font-bold text-white">GSTIN</span>
          <span className="text-emerald-400">VERIFIED</span>
        </div>
        <div className="p-3 rounded bg-slate-900 border border-slate-800 text-center">
          <span className="block font-bold text-white">MCA CIN</span>
          <span className="text-emerald-400">VERIFIED</span>
        </div>
        <div className="p-3 rounded bg-slate-900 border border-slate-800 text-center">
          <span className="block font-bold text-white">PAN</span>
          <span className="text-emerald-400">VERIFIED</span>
        </div>
        <div className="p-3 rounded bg-slate-900 border border-slate-800 text-center">
          <span className="block font-bold text-white">UDYAM</span>
          <span className="text-emerald-400">VERIFIED</span>
        </div>
        <div className="p-3 rounded bg-slate-900 border border-slate-800 text-center">
          <span className="block font-bold text-white">EPFO</span>
          <span className="text-blue-400">CACHED</span>
        </div>
        <div className="p-3 rounded bg-slate-900 border border-slate-800 text-center">
          <span className="block font-bold text-white">DEBARMENT</span>
          <span className="text-emerald-400">VERIFIED</span>
        </div>
      </div>
    )
  },
  {
    title: "7. Network Intelligence (Cytoscape.js)",
    subtitle: "Entity Relationship Graph & Shared Attribute Signals",
    content: (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-950 font-mono text-xs text-amber-300 space-y-2">
        <div className="font-bold text-white">Entity Relationship Signal Detected:</div>
        <p className="text-slate-300">Potential shared-control relationship detected: Shared Corporate Director (Vikramaditya Mehta) registered across 2 bidding entities.</p>
        <div className="p-2 rounded bg-slate-900 text-slate-400 text-[11px]">Neutral Signal Terminology Enforced · No Accusatory Fraud Labels</div>
      </div>
    )
  },
  {
    title: "8. Anomaly Intelligence Engine",
    subtitle: "Unsupervised IsolationForest (9 Feature Vectors)",
    content: (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 space-y-3 font-mono text-xs">
        <div className="flex justify-between border-b border-slate-800 pb-2">
          <span>PROCUREMENT ANOMALY SCORE:</span>
          <span className="text-amber-400 font-bold">0.78 (Elevated Advisory Signal)</span>
        </div>
        <div className="text-[11px] text-slate-400 space-y-1">
          <div>Top Contributing Factors:</div>
          <div className="text-slate-200">1. Shared registered address count (3 entities)</div>
          <div className="text-slate-200">2. Verification mismatch count (1 mismatch)</div>
        </div>
      </div>
    )
  },
  {
    title: "9. Policy Copilot & Citation Engine",
    subtitle: "Evidence-Grounded Policy RAG (GFR 2017 & GeM Manual)",
    content: (
      <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 space-y-3 text-xs">
        <div className="font-mono font-bold text-white">Question: &ldquo;What does GFR Rule 149 mandate?&rdquo;</div>
        <p className="text-slate-300 leading-relaxed">&ldquo;Procurement of Goods and Services by Ministries or Departments will be mandatory for Goods or Services available on GeM.&rdquo;</p>
        <div className="font-mono text-blue-400 text-[11px]">[Citation: GFR 2017 | Section: Rule 149 | Page: 82]</div>
      </div>
    )
  },
  {
    title: "10. WOW Scenario S — Officer Override",
    subtitle: "Mandatory Written Justification Protocol",
    content: (
      <div className="p-4 rounded-xl border border-amber-800/80 bg-amber-950/20 font-mono text-xs space-y-2">
        <div className="font-bold text-amber-300">System Recommendation: MANUAL_REVIEW_REQUIRED</div>
        <div className="font-bold text-emerald-400">Officer Decision: APPROVED</div>
        <div className="p-2 rounded bg-slate-950 text-slate-300 border border-slate-850">
          Written Justification: &ldquo;Bidder submitted supplementary tax clearance certificate and audited balance sheet verifying solvency.&rdquo;
        </div>
        <div className="text-amber-400 text-[10px]">Override Recorded (`is_override = True`) & Signed into Audit Hash Ledger</div>
      </div>
    )
  },
  {
    title: "11. WOW Scenario W — Tamper-Evident Audit Ledger",
    subtitle: "Cryptographic SHA-256 Event Chain Integrity",
    content: (
      <div className="p-4 rounded-xl border border-emerald-800/80 bg-emerald-950/20 font-mono text-xs space-y-2">
        <div className="flex justify-between font-bold text-emerald-300">
          <span>GLOBAL AUDIT LEDGER STATUS:</span>
          <span>VALID</span>
        </div>
        <div className="p-2 rounded bg-slate-950 text-slate-400 text-[10px]">
          event_hash = SHA-256(action | entity_id | payload | timestamp | previous_hash)
        </div>
        <p className="text-slate-300">Any manual database alteration breaks the hash chain, triggering automated tamper alert (`status: INVALID`).</p>
      </div>
    )
  },
  {
    title: "12. Complete 23 Scenarios Registry",
    subtitle: "Scenarios A through W Fully Seeded & Executable",
    content: (
      <div className="grid grid-cols-4 gap-2 font-mono text-[10px] text-center">
        {['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W'].map(c => (
          <div key={c} className="p-2 rounded bg-slate-900 border border-slate-800 text-blue-300 font-bold">
            Scenario {c}
          </div>
        ))}
      </div>
    )
  },
  {
    title: "13. System Architecture & Tech Stack",
    subtitle: "Production-Grade Micro-Services Architecture",
    content: (
      <div className="grid grid-cols-2 gap-4 font-mono text-xs text-slate-300">
        <div className="p-3 rounded bg-slate-900 border border-slate-800 space-y-1">
          <span className="font-bold text-white">BACKEND & STORAGE</span>
          <div>FastAPI + Async SQLAlchemy</div>
          <div>PostgreSQL + pgvector</div>
          <div>Redis + MinIO Object Storage</div>
        </div>
        <div className="p-3 rounded bg-slate-900 border border-slate-800 space-y-1">
          <span className="font-bold text-white">FRONTEND & AI</span>
          <div>Next.js 14 App Router + TS</div>
          <div>Cytoscape.js Network Graph</div>
          <div>IsolationForest Anomaly Model</div>
        </div>
      </div>
    )
  },
  {
    title: "14. PROCUREX Impact Summary",
    subtitle: "Verify. Explain. Detect. Decide.",
    content: (
      <div className="text-center space-y-4">
        <div className="text-2xl font-mono font-extrabold text-white">From Procurement Documents to Evidence-Grounded Decisions.</div>
        <div className="grid grid-cols-3 gap-3 font-mono text-xs">
          <div className="p-3 rounded bg-blue-950/60 border border-blue-800 text-blue-300">90% Faster Review</div>
          <div className="p-3 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-300">100% Audit Integrity</div>
          <div className="p-3 rounded bg-purple-950/60 border border-purple-800 text-purple-300">Zero Unsafe AI Decisions</div>
        </div>
      </div>
    )
  }
];

export default function PresentationModePage() {
  const [currentIdx, setCurrentIdx] = useState(0);

  const slide = SLIDES[currentIdx];

  return (
    <div className="flex h-screen w-screen flex-col bg-slate-950 text-slate-100 p-8 select-none">
      {/* Top Bar */}
      <div className="flex items-center justify-between border-b border-slate-850 pb-4">
        <Link href="/demo" className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="h-4 w-4" />
          <span>Exit Presentation</span>
        </Link>
        <div className="font-mono text-xs font-bold text-blue-400 uppercase tracking-widest flex items-center gap-2">
          <Monitor className="h-4 w-4" />
          <span>PROCUREX Evaluator Presentation Deck</span>
        </div>
        <div className="font-mono text-xs text-slate-400">
          Slide <span className="text-white font-bold">{currentIdx + 1}</span> of {SLIDES.length}
        </div>
      </div>

      {/* Main Slide Content */}
      <div className="flex-1 flex flex-col justify-center max-w-4xl mx-auto w-full py-8">
        <div className="text-center space-y-2 mb-8">
          <h1 className="font-mono text-3xl font-black tracking-tight text-white">{slide.title}</h1>
          <p className="text-sm font-mono text-blue-400">{slide.subtitle}</p>
        </div>
        <div>
          {slide.content}
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="flex items-center justify-between border-t border-slate-850 pt-4">
        <button
          disabled={currentIdx === 0}
          onClick={() => setCurrentIdx(currentIdx - 1)}
          className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900 px-4 py-2 text-xs font-mono font-bold text-slate-300 hover:bg-slate-850 disabled:opacity-30"
        >
          <ChevronLeft className="h-4 w-4" />
          <span>Previous Slide</span>
        </button>

        <div className="flex gap-1.5">
          {SLIDES.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentIdx(i)}
              className={`h-2 rounded-full transition-all ${i === currentIdx ? 'w-8 bg-blue-500' : 'w-2 bg-slate-800 hover:bg-slate-700'}`}
            />
          ))}
        </div>

        <button
          disabled={currentIdx === SLIDES.length - 1}
          onClick={() => setCurrentIdx(currentIdx + 1)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-mono font-bold text-white hover:bg-blue-500 disabled:opacity-30"
        >
          <span>Next Slide</span>
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
