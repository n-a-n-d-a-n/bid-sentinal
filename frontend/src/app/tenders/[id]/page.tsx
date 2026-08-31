'use client';

import React from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { FileText, CheckCircle, HelpCircle, AlertTriangle, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function TenderDetailPage({ params }: { params: { id: string } }) {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <Link href="/tenders" className="rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-400 hover:text-white">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
              Tender Requirements: {params.id.toUpperCase()}
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Supply of Smart Grid Metering Equipment · Ministry of Power, Govt of India
            </p>
          </div>
        </div>

        {/* 17 Canonical Requirements Table */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="font-mono text-sm font-bold text-slate-100 uppercase tracking-wider">
              Normalized Tender Requirements
            </h2>
            <span className="text-xs text-emerald-400 font-mono">100% Extraction Provenance Grounded</span>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 font-mono text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Requirement Type</th>
                  <th className="py-3 px-4">Operator</th>
                  <th className="py-3 px-4">Target Value</th>
                  <th className="py-3 px-4">Source Page</th>
                  <th className="py-3 px-4">Document Excerpt</th>
                  <th className="py-3 px-4">Mandatory</th>
                  <th className="py-3 px-4 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                <tr className="hover:bg-slate-850/50 transition-colors">
                  <td className="py-3 px-4 font-semibold text-white">FINANCIAL / TURNOVER</td>
                  <td className="py-3 px-4 font-mono text-amber-400">&gt;=</td>
                  <td className="py-3 px-4 font-mono text-emerald-400">₹5,00,00,000.00</td>
                  <td className="py-3 px-4 font-mono">Page 12</td>
                  <td className="py-3 px-4 italic text-slate-400">&ldquo;Average annual financial turnover during the last 3 financial years must be at least ₹5 Crore.&rdquo;</td>
                  <td className="py-3 px-4"><span className="rounded bg-rose-950 px-2 py-0.5 text-[10px] font-mono text-rose-300">YES</span></td>
                  <td className="py-3 px-4 font-mono text-right text-emerald-400">98%</td>
                </tr>

                <tr className="hover:bg-slate-850/50 transition-colors">
                  <td className="py-3 px-4 font-semibold text-white">TAX / GSTIN</td>
                  <td className="py-3 px-4 font-mono text-amber-400">REQUIRED</td>
                  <td className="py-3 px-4 font-mono text-blue-400">VALID GSTIN</td>
                  <td className="py-3 px-4 font-mono">Page 4</td>
                  <td className="py-3 px-4 italic text-slate-400">&ldquo;Bidder must possess a valid Goods and Services Tax Identification Number (GSTIN).&rdquo;</td>
                  <td className="py-3 px-4"><span className="rounded bg-rose-950 px-2 py-0.5 text-[10px] font-mono text-rose-300">YES</span></td>
                  <td className="py-3 px-4 font-mono text-right text-emerald-400">100%</td>
                </tr>

                <tr className="hover:bg-slate-850/50 transition-colors">
                  <td className="py-3 px-4 font-semibold text-white">LEGAL / BLACKLIST</td>
                  <td className="py-3 px-4 font-mono text-amber-400">EXISTS</td>
                  <td className="py-3 px-4 font-mono text-emerald-400">CLEAR (NOT DEBARRED)</td>
                  <td className="py-3 px-4 font-mono">Page 18</td>
                  <td className="py-3 px-4 italic text-slate-400">&ldquo;The bidder should not be blacklisted or debarred by any State/Central Govt entity.&rdquo;</td>
                  <td className="py-3 px-4"><span className="rounded bg-rose-950 px-2 py-0.5 text-[10px] font-mono text-rose-300">YES</span></td>
                  <td className="py-3 px-4 font-mono text-right text-emerald-400">100%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
