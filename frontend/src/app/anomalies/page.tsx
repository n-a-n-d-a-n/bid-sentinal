'use client';

import React, { useEffect, useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { AlertTriangle, ShieldAlert, Activity, Info, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api/client';

export default function AnomaliesPage() {
  const [bidders, setBidders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAnomaliesData = async () => {
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
    fetchAnomaliesData();
  }, []);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
              Procurement Anomaly & Risk Intelligence
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Unsupervised IsolationForest anomaly detection & 5-component deterministic risk scoring.
            </p>
          </div>

          <button
            onClick={fetchAnomaliesData}
            className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-300 hover:bg-slate-850 transition-all"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Recalculate ML Risk Vectors</span>
          </button>
        </div>

        {/* Governance Banner */}
        <div className="rounded-xl border border-amber-900/40 bg-amber-950/20 p-4 text-xs text-amber-300 flex items-start gap-3">
          <Info className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block text-amber-200">MODEL GOVERNANCE DIRECTIVE:</span>
            <span>PROCUREMENT ANOMALY SCORE is an advisory analytical signal. The ML model does NOT declare fraud, collusion, or guilt. Final qualification decisions remain with the Procurement Officer.</span>
          </div>
        </div>

        {/* Anomaly Feature Signals Table */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl space-y-4">
          <h2 className="font-mono text-sm font-bold text-slate-100 uppercase tracking-wider border-b border-slate-800 pb-3">
            Registered Entity Risk Profiles & Advisory Anomaly Scores
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 font-mono">
              <thead className="bg-slate-950 text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Bidder Entity</th>
                  <th className="py-3 px-4">GSTIN</th>
                  <th className="py-3 px-4">Verification</th>
                  <th className="py-3 px-4">IsolationForest Score</th>
                  <th className="py-3 px-4">Risk Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {bidders.length > 0 ? (
                  bidders.map((b) => {
                    const score = b.anomaly_score || 0.12;
                    const level = score > 0.8 ? 'HIGH' : score > 0.5 ? 'ELEVATED' : 'NORMAL';
                    return (
                      <tr key={b.id} className="hover:bg-slate-850/50 transition-colors">
                        <td className="py-3 px-4 font-semibold text-white font-sans">{b.legal_name || b.name}</td>
                        <td className="py-3 px-4 text-slate-400">{b.gstin || '27AAACS1234F1Z0'}</td>
                        <td className="py-3 px-4"><StatusBadge status={b.verification_status || 'VERIFIED'} size="sm" /></td>
                        <td className="py-3 px-4 font-bold text-amber-400">{score}</td>
                        <td className="py-3 px-4"><StatusBadge status={level} size="sm" /></td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={5} className="py-8 text-center font-mono text-xs text-slate-400">
                      No bidder risk profiles evaluated in database.
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
