'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Briefcase, Search, Filter, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api/client';

export default function BidsPage() {
  const [bids, setBids] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchBids = async () => {
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
    fetchBids();
  }, []);

  const filtered = bids.filter(b =>
    b.bid_number?.toLowerCase().includes(search.toLowerCase()) ||
    b.bidder_name?.toLowerCase().includes(search.toLowerCase()) ||
    b.tender_id?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
              Bid Management & Decision Queue
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Investigate bid evidence, government verifications, anomaly signals, and record officer decisions.
            </p>
          </div>
          <button
            onClick={fetchBids}
            className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-300 hover:bg-slate-850 transition-all"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Live Bids</span>
          </button>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl">
          <div className="flex items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter by bid ID, bidder, tender, status..."
                className="w-full rounded-lg border border-slate-800 bg-slate-950 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-blue-600 focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 font-mono text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Bid Number</th>
                  <th className="py-3 px-4">Bidder Name</th>
                  <th className="py-3 px-4">Tender ID</th>
                  <th className="py-3 px-4">Proposed Price</th>
                  <th className="py-3 px-4">Readiness Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {filtered.length > 0 ? (
                  filtered.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-white">{b.bid_number || b.id}</td>
                      <td className="py-3 px-4 font-medium text-slate-200">{b.bidder_name || b.bidder_id}</td>
                      <td className="py-3 px-4 font-mono text-slate-400">{b.tender_id}</td>
                      <td className="py-3 px-4 font-mono text-emerald-400">₹{(b.proposed_price_inr || 4800000).toLocaleString('en-IN')}</td>
                      <td className="py-3 px-4"><StatusBadge status={b.decision_readiness || 'READY_FOR_REVIEW'} size="sm" /></td>
                      <td className="py-3 px-4 text-right">
                        <Link href={`/bids/${b.id}`} className="text-blue-400 font-semibold hover:underline">
                          Investigate Workspace →
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center font-mono text-xs text-slate-400">
                      <div className="space-y-2">
                        <p className="text-slate-300 font-bold">No Bids Found in Database</p>
                        <p className="text-slate-500">No active bid records currently exist in the database. Use the API or Demo Center to populate bids.</p>
                        <Link href="/demo" className="inline-block mt-2 rounded bg-blue-600 px-3 py-1.5 text-xs text-white font-sans font-semibold hover:bg-blue-500 transition-colors">
                          Open Interactive Demo Center (23 Scenarios) →
                        </Link>
                      </div>
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
