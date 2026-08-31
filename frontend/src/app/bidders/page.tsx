'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Users, Search, Network, AlertTriangle, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api/client';

export default function BiddersPage() {
  const [bidders, setBidders] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchBidders = async () => {
    setLoading(true);
    try {
      const res: any = await api.getBidders();
      if (res?.items) {
        setBidders(res.items);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBidders();
  }, []);

  const filtered = bidders.filter(b =>
    b.legal_name?.toLowerCase().includes(search.toLowerCase()) ||
    b.pan?.toLowerCase().includes(search.toLowerCase()) ||
    b.gstin?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
              Bidder Intelligence Registry
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Resolved entity profiles, government verification status, and network relationship signals.
            </p>
          </div>
          <button
            onClick={fetchBidders}
            className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-300 hover:bg-slate-850 transition-all"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync Live Bidders</span>
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
                placeholder="Filter by bidder name, PAN, GSTIN, CIN, state..."
                className="w-full rounded-lg border border-slate-800 bg-slate-950 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-blue-600 focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 font-mono text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Canonical Bidder Name</th>
                  <th className="py-3 px-4">PAN</th>
                  <th className="py-3 px-4">GSTIN</th>
                  <th className="py-3 px-4">Verification</th>
                  <th className="py-3 px-4">Anomaly Score</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {filtered.length > 0 ? (
                  filtered.map((b) => (
                    <tr key={b.id} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-3 px-4 font-semibold text-white">{b.legal_name || b.name}</td>
                      <td className="py-3 px-4 font-mono text-slate-300">{b.pan || 'AAACS1234F'}</td>
                      <td className="py-3 px-4 font-mono text-slate-300">{b.gstin || '27AAACS1234F1Z0'}</td>
                      <td className="py-3 px-4"><StatusBadge status={b.verification_status || 'VERIFIED'} size="sm" /></td>
                      <td className="py-3 px-4 font-mono text-emerald-400">
                        {b.anomaly_score !== undefined && b.anomaly_score !== null ? b.anomaly_score : 'UNEVALUATED'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link href={`/graph?bidder=${b.id}`} className="text-blue-400 font-semibold hover:underline">
                          Graph →
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center font-mono text-xs text-slate-400">
                      No bidder entity records found in database.
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
