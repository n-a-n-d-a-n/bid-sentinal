# PROCUREX Frontend Architecture

## Overview
The PROCUREX frontend is built using **Next.js App Router**, **TypeScript**, **Tailwind CSS**, and **Cytoscape.js**.

## Core Directory Structure
```
frontend/src/
├── app/
│   ├── layout.tsx                # Root layout & TanStack Query Provider
│   ├── page.tsx / dashboard/     # Mission Control Overview & KPIs
│   ├── login/                    # Authentication & Quick Evaluator Role selection
│   ├── tenders/                  # Requirement Intelligence
│   ├── bidders/                  # Bidder Registry & Entity Profiles
│   ├── bids/                     # 10-Tab Bid Investigation Workspace & Decision Center
│   ├── documents/                # PyMuPDF Document Intelligence
│   ├── verification/             # 10 Government Provider Resilience Center
│   ├── anomalies/                # IsolationForest Feature Signals
│   ├── graph/                    # Fullscreen Cytoscape Procurement Network Visualizer
│   ├── policy/                   # Evidence-Grounded Policy Copilot (GFR 2017 & GeM Manual)
│   ├── decisions/                # Decision Governance Center
│   ├── audit/                    # SHA-256 Tamper-Evident Audit Ledger Explorer
│   └── demo/                     # SIH Interactive Demo Center (Scenarios A - W)
├── components/
│   ├── common/                   # StatusBadge, MetricCard, EvidenceCard, CitationBadge
│   ├── graph/                    # CytoscapeGraph interactive visualizer
│   └── layout/                   # Sidebar, Header, AppLayout
└── lib/api/                      # Typed Axios API Client & Endpoint bindings
```
