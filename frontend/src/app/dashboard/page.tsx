'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppLayout } from '@/components/layout/AppLayout';
import { MetricCard } from '@/components/common/MetricCard';
import { StatusBadge } from '@/components/common/StatusBadge';
import { api } from '@/lib/api/client';
import {
  FileCheck2,
  Briefcase,
  AlertTriangle,
  Building2,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  Activity,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  XCircle,
  RefreshCw,
} from 'lucide-react';

export default function DashboardPage() {
  const [bids, setBids] = useState<any[]>([]);
  const [tenders, setTenders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setFetchError(null);
    try {
      const [bidsRes, tendersRes]: [any, any] = await Promise.all([
        api.getBids(),
        api.getTenders(),
      ]);

      setBids(bidsRes?.items || []);
      setTenders(tendersRes?.items || []);
    } catch (err: any) {
      console.error('API load error', err);
      setFetchError(err.message || 'API Connection Unavailable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const totalBids = bids.length;
  const readyCount = bids.filter(b => b.decision_readiness === 'READY_FOR_REVIEW').length;
  const reviewCount = bids.filter(b => b.decision_readiness === 'MANUAL_REVIEW_REQUIRED').length;
  const blockedCount = bids.filter(b => b.decision_readiness === 'BLOCKED').length;
  const incompleteCount = bids.filter(b => b.decision_readiness === 'INCOMPLETE').length;

  const backendActive = !fetchError && !loading;

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header Title */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
                Procurement Intelligence Overview
              </h1>
              {backendActive ? (
                <span className="rounded bg-emerald-950 px-2.5 py-0.5 text-[10px] font-mono text-emerald-400 border border-emerald-800">
                  LIVE BACKEND CONNECTED
                </span>
              ) : (
                <span className="rounded bg-rose-950 px-2.5 py-0.5 text-[10px] font-mono text-rose-400 border border-rose-800">
                  API UNAVAILABLE
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-slate-400">
              Evidence-grounded analysis & transparent decision governance for GeM procurement.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchDashboardData}
              className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-300 hover:bg-slate-850 transition-all"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <Link
              href="/demo"
              className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-emerald-900/50 hover:bg-emerald-500 transition-all"
            >
              <span>Launch Demo Center (23 Scenarios)</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>

        {/* Top Mission Control KPIs */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Active Tenders"
            value={loading ? '...' : fetchError ? 'UNAVAILABLE' : String(tenders.length)}
            subtitle="GeM Procurement Catalog"
            icon={FileCheck2}
            variant="blue"
          />
          <MetricCard
            title="Bids Under Review"
            value={loading ? '...' : fetchError ? 'UNAVAILABLE' : String(bids.length)}
            subtitle="Pending Officer Decision"
            icon={Briefcase}
            variant="slate"
          />
          <MetricCard
            title="Manual Reviews Required"
            value={loading ? '...' : fetchError ? 'UNAVAILABLE' : String(reviewCount)}
            subtitle="Contradiction / Fuzzy Match"
            icon={AlertTriangle}
            variant="amber"
          />
          <MetricCard
            title="Critical Exceptions"
            value={loading ? '...' : fetchError ? 'UNAVAILABLE' : String(blockedCount)}
            subtitle="Identity Mismatch / Blacklist"
            icon={ShieldAlert}
            variant="rose"
          />
        </div>

        {/* Decision Readiness Distribution */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-blue-400" />
              <h2 className="font-mono text-sm font-bold text-slate-100 uppercase tracking-wider">
                Decision Readiness Distribution
              </h2>
            </div>
            <span className="text-xs text-slate-400 font-mono">{totalBids} Total Bids Evaluated</span>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-emerald-900/40 bg-emerald-950/20 p-4">
              <div className="flex items-center justify-between text-xs text-emerald-400">
                <span className="font-semibold">READY FOR REVIEW</span>
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <div className="mt-2 text-2xl font-bold font-mono text-white">{readyCount}</div>
              <p className="mt-1 text-[11px] text-slate-400">All mandatory requirements pass + verifications clear.</p>
            </div>

            <div className="rounded-lg border border-amber-900/40 bg-amber-950/20 p-4">
              <div className="flex items-center justify-between text-xs text-amber-400">
                <span className="font-semibold">MANUAL REVIEW</span>
                <AlertCircle className="h-4 w-4" />
              </div>
              <div className="mt-2 text-2xl font-bold font-mono text-white">{reviewCount}</div>
              <p className="mt-1 text-[11px] text-slate-400">Variances or fuzzy matches require officer investigation.</p>
            </div>

            <div className="rounded-lg border border-rose-900/40 bg-rose-950/20 p-4">
              <div className="flex items-center justify-between text-xs text-rose-400">
                <span className="font-semibold">BLOCKED</span>
                <XCircle className="h-4 w-4" />
              </div>
              <div className="mt-2 text-2xl font-bold font-mono text-white">{blockedCount}</div>
              <p className="mt-1 text-[11px] text-slate-400">Critical identity mismatch or debarment detected.</p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold">INCOMPLETE</span>
                <HelpCircle className="h-4 w-4" />
              </div>
              <div className="mt-2 text-2xl font-bold font-mono text-white">{incompleteCount}</div>
              <p className="mt-1 text-[11px] text-slate-400">Missing mandatory document or verification evidence.</p>
            </div>
          </div>
        </div>

        {/* Recent Investigations Table */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="font-mono text-sm font-bold text-slate-100 uppercase tracking-wider">
              Recent Procurement Investigations
            </h2>
            <Link href="/bids" className="text-xs text-blue-400 hover:underline">
              View All Bids →
            </Link>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 font-mono text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Bidder</th>
                  <th className="py-3 px-4">Tender ID</th>
                  <th className="py-3 px-4">Compliance</th>
                  <th className="py-3 px-4">Verification</th>
                  <th className="py-3 px-4">Anomaly Score</th>
                  <th className="py-3 px-4">Readiness</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {bids.length > 0 ? (
                  bids.slice(0, 5).map((bid) => (
                    <tr key={bid.id} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-3 px-4 font-semibold text-white">{bid.bidder_name || bid.bidder_id}</td>
                      <td className="py-3 px-4 font-mono text-slate-400">{bid.tender_id}</td>
                      <td className="py-3 px-4"><StatusBadge status={bid.compliance_status || 'PASS'} size="sm" /></td>
                      <td className="py-3 px-4"><StatusBadge status={bid.verification_status || 'VERIFIED'} size="sm" /></td>
                      <td className="py-3 px-4 font-mono text-emerald-400">{bid.anomaly_score || 0.12}</td>
                      <td className="py-3 px-4"><StatusBadge status={bid.decision_readiness || 'READY_FOR_REVIEW'} size="sm" /></td>
                      <td className="py-3 px-4 text-right">
                        <Link href={`/bids/${bid.id}`} className="text-blue-400 font-semibold hover:underline">
                          Investigate →
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="py-8 text-center font-mono text-xs text-slate-400">
                      No recent bid investigations recorded in database. Use Demo Center to load demonstration scenarios.
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
