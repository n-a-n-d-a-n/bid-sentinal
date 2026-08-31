'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FileCheck2,
  Users,
  Briefcase,
  FileText,
  Building2,
  AlertTriangle,
  Network,
  BookOpenCheck,
  Scale,
  ShieldAlert,
  PlayCircle,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { clsx } from 'clsx';

const NAV_ITEMS = [
  { label: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Tenders', href: '/tenders', icon: FileCheck2 },
  { label: 'Bidders', href: '/bidders', icon: Users },
  { label: 'Bids & Reviews', href: '/bids', icon: Briefcase },
  { label: 'Documents', href: '/documents', icon: FileText },
  { label: 'Verification', href: '/verification', icon: Building2 },
  { label: 'Risk & Anomalies', href: '/anomalies', icon: AlertTriangle },
  { label: 'Procurement Graph', href: '/graph', icon: Network },
  { label: 'Policy Copilot', href: '/policy', icon: BookOpenCheck },
  { label: 'Decision Center', href: '/decisions', icon: Scale },
  { label: 'Audit Ledger', href: '/audit', icon: ShieldAlert },
  { label: 'Demo Center', href: '/demo', icon: PlayCircle, highlight: true },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={clsx(
        'relative flex flex-col border-r border-slate-850 bg-slate-950 transition-all duration-300 z-30',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo Header */}
      <div className="flex h-16 items-center justify-between border-b border-slate-850 px-4">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white font-bold shadow-lg shadow-blue-900/40">
              P
            </div>
            <div>
              <span className="font-mono text-lg font-extrabold tracking-wider text-white">PROCUREX</span>
              <span className="block text-[9px] uppercase tracking-widest text-slate-400">Government Procurement Intelligence</span>
            </div>
          </Link>
        )}
        {collapsed && (
          <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 font-bold text-white">
            P
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="rounded-md p-1.5 text-slate-400 hover:bg-slate-900 hover:text-white"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== '/dashboard');

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                'flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs font-medium transition-all cursor-pointer select-none',
                isActive
                  ? 'bg-blue-950/80 text-blue-300 border border-blue-800/60 shadow-sm font-semibold'
                  : 'text-slate-400 hover:bg-slate-900/80 hover:text-slate-200',
                item.highlight && !isActive && 'text-emerald-400 font-semibold'
              )}
            >
              <Icon className={clsx('h-4 w-4 flex-shrink-0', isActive ? 'text-blue-400' : 'text-slate-400')} />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer Status */}
      {!collapsed && (
        <div className="border-t border-slate-850 p-3">
          <div className="flex items-center gap-2 rounded-lg bg-slate-900/80 p-2 border border-slate-850">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <div className="text-[11px]">
              <span className="block font-medium text-slate-200">Procurement Evaluator Sandbox</span>
              <span className="text-slate-400">All 23 Scenarios Ready</span>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
};
