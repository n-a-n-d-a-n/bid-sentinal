'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { AppLayout } from '@/components/layout/AppLayout';
import { CytoscapeGraph } from '@/components/graph/CytoscapeGraph';
import { Network, Info, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api/client';

const FULL_GRAPH_DATA = {
  nodes: [
    { data: { id: 'b1', label: 'Shakti Infra Pvt Ltd', type: 'BIDDER' } },
    { data: { id: 'b2', label: 'Alpha Infra Solutions', type: 'BIDDER' } },
    { data: { id: 'b3', label: 'Beta Power Ltd', type: 'BIDDER' } },
    { data: { id: 'dir1', label: 'Vikramaditya Mehta', type: 'DIRECTOR' } },
    { data: { id: 'dir2', label: 'Rajesh Kumar', type: 'DIRECTOR' } },
    { data: { id: 'addr1', label: 'Plot 99, Industrial Complex, Pune', type: 'ADDRESS' } },
    { data: { id: 'bank1', label: 'HDFC-001122334455', type: 'BANK_ACCOUNT' } },
    { data: { id: 't1', label: 'TNDR-2026-1042', type: 'TENDER' } },
  ],
  edges: [
    { data: { source: 'b1', target: 'dir1', relationship: 'BIDDER_HAS_DIRECTOR' } },
    { data: { source: 'b2', target: 'dir1', relationship: 'BIDDER_HAS_DIRECTOR' } },
    { data: { source: 'b1', target: 'addr1', relationship: 'BIDDER_HAS_ADDRESS' } },
    { data: { source: 'b2', target: 'addr1', relationship: 'BIDDER_HAS_ADDRESS' } },
    { data: { source: 'b3', target: 'addr1', relationship: 'BIDDER_HAS_ADDRESS' } },
    { data: { source: 'b1', target: 'bank1', relationship: 'BIDDER_HAS_BANK_ACCOUNT' } },
    { data: { source: 'b1', target: 't1', relationship: 'BIDDER_SUBMITTED_BID' } },
    { data: { source: 'b2', target: 't1', relationship: 'BIDDER_SUBMITTED_BID' } },
  ],
};

function GraphContent() {
  const searchParams = useSearchParams();
  const bidderId = searchParams.get('bidder');
  const bidId = searchParams.get('bid');

  const [graphData, setGraphData] = useState<any>(FULL_GRAPH_DATA);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadGraph() {
      if (!bidderId && !bidId) return;
      setLoading(true);
      try {
        let res: any = null;
        if (bidId) {
          res = await api.getBidGraph(bidId).catch(() => null);
        } else if (bidderId) {
          res = await api.getBidderGraph(bidderId).catch(() => null);
        }
        if (res && res.nodes && res.nodes.length > 0) {
          setGraphData(res);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [bidderId, bidId]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
            <Network className="h-6 w-6 text-blue-400" />
            Procurement Network Visualizer
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            Interactive Cytoscape.js visualization of bidders, directors, addresses, bank accounts, and tenders.
          </p>
        </div>
        {(bidderId || bidId) && (
          <span className="rounded bg-blue-950 px-3 py-1 font-mono text-xs text-blue-300 border border-blue-800">
            Filter: {bidderId ? `Bidder (${bidderId})` : `Bid (${bidId})`}
          </span>
        )}
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-950 shadow-2xl">
        <CytoscapeGraph data={graphData} height="580px" />
      </div>
    </div>
  );
}

export default function FullGraphPage() {
  return (
    <AppLayout>
      <Suspense fallback={<div className="p-6 text-slate-400 font-mono text-xs">Loading Graph Engine...</div>}>
        <GraphContent />
      </Suspense>
    </AppLayout>
  );
}
