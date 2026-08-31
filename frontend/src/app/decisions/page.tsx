'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Scale, CheckCircle2, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api/client';

export default function DecisionsPage() {
  const [bids, setBids] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDecisionsData = async () => {
    setLoading(true);
    try {
      const res: any = await api.getBids();
      if (res?.items) {
        setBids(res.items);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisionsData();
  }, []);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
              <Scale className="h-6 w-6 text-blue-400" />
              Officer Decision Governance Center
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Formal state machine review queue, mandatory justification tracking, and officer override governance.
            </p>
          </div>

          <button
            onClick={fetchDecisionsData}
            className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-300 hover:bg-slate-850 transition-all"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Decision Queue</span>
          </button>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl">
          <h2 className="font-mono text-sm font-bold text-slate-100 uppercase tracking-wider border-b border-slate-800 pb-3">
            Officer Decision Queue
          </h2>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 font-mono text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Bid ID</th>
                  <th className="py-3 px-4">Bidder</th>
                  <th className="py-3 px-4">System Rec</th>
                  <th className="py-3 px-4">Officer Decision</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850 font-mono">
                {bids.length > 0 ? (
                  bids.map((b) => (
                    <tr key={b.id}>
                      <td className="py-3 px-4 font-bold text-white">{b.bid_number || b.id}</td>
                      <td className="py-3 px-4 font-sans font-medium text-slate-200">{b.bidder_name || b.bidder_id}</td>
                      <td className="py-3 px-4"><StatusBadge status={b.decision_readiness || 'MANUAL_REVIEW_REQUIRED'} size="sm" /></td>
                      <td className="py-3 px-4"><StatusBadge status={b.status || 'PENDING_OFFICER_REVIEW'} size="sm" /></td>
                      <td className="py-3 px-4 text-right font-sans">
                        <Link href={`/bids/${b.id}`} className="text-blue-400 font-semibold hover:underline">
                          Review Record →
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-8 text-center font-mono text-xs text-slate-400">
                      No pending officer decisions in review queue.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
