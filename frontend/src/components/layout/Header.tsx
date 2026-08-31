'use client';

import React from 'react';
import Link from 'next/link';
import { Search, Bell, ShieldCheck, UserCheck, Play } from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-slate-850 bg-slate-950/90 px-6 backdrop-blur-md">
      {/* Global Search */}
      <div className="flex items-center gap-3 w-96">
        <div className="relative w-full">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search tenders, bidders, GSTIN, PAN, policy rules..."
            className="w-full rounded-lg border border-slate-800 bg-slate-900/80 py-2 pl-9 pr-4 text-xs text-white placeholder-slate-400 focus:border-blue-600 focus:outline-none"
          />
        </div>
      </div>

      {/* Right Header Actions */}
      <div className="flex items-center gap-4">
        {/* Quick Demo Mode Badge */}
        <Link
          href="/demo"
          className="flex items-center gap-1.5 rounded-lg border border-emerald-800/60 bg-emerald-950/80 px-3 py-1.5 text-xs font-mono font-medium text-emerald-300 hover:bg-emerald-900/80 transition-all shadow-sm shadow-emerald-950"
        >
          <Play className="h-3.5 w-3.5 fill-current" />
          <span>Interactive Demo Center</span>
        </Link>

        {/* System Health */}
        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span className="font-mono text-emerald-400">HEALTHY</span>
        </div>

        {/* Divider */}
        <div className="h-4 w-px bg-slate-800" />

        {/* Officer Profile */}
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 border border-slate-700 text-xs font-bold text-white">
            PO
          </div>
          <div className="text-left text-xs">
            <span className="block font-medium text-slate-200">Procurement Officer</span>
            <span className="text-[10px] font-mono text-blue-400 uppercase tracking-wider">OFFICER_ROLE</span>
          </div>
        </div>
      </div>
    </header>
  );
};
