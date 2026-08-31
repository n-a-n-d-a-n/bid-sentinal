'use client';

import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Building2, ShieldCheck, RefreshCw, Zap, CheckCircle2 } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

const INITIAL_PROVIDERS = [
  { name: 'GST', full: 'Goods and Services Tax Network', status: 'VERIFIED', rateLimit: '60/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'MCA', full: 'Ministry of Corporate Affairs (CIN/Directors)', status: 'VERIFIED', rateLimit: '30/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'PAN', full: 'Income Tax Department (PAN Verification)', status: 'VERIFIED', rateLimit: '60/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'UDYAM', full: 'MSME Udyam Registration Portal', status: 'VERIFIED', rateLimit: '60/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'EPFO', full: 'Employees Provident Fund Organisation', status: 'VERIFIED', rateLimit: '30/min', cbState: 'CLOSED', cache: 'CACHED' },
  { name: 'ESIC', full: 'Employees State Insurance Corporation', status: 'VERIFIED', rateLimit: '30/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'DIGILOCKER', full: 'DigiLocker Document Verification', status: 'VERIFIED', rateLimit: '60/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'BIS', full: 'Bureau of Indian Standards', status: 'VERIFIED', rateLimit: '30/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'GEM', full: 'Government e-Marketplace Seller Registry', status: 'VERIFIED', rateLimit: '60/min', cbState: 'CLOSED', cache: 'LIVE' },
  { name: 'BLACKLIST', full: 'Centralized Govt Debarment Registry', status: 'VERIFIED', rateLimit: '120/min', cbState: 'CLOSED', cache: 'LIVE' },
];

export default function VerificationPage() {
  const [providers, setProviders] = useState(INITIAL_PROVIDERS);
  const [testing, setTesting] = useState(false);

  const handleTestAdapters = async () => {
    setTesting(true);
    try {
      const res: any = await apiClient.get('/verification/adapters');
      if (res?.adapters) {
        setProviders(res.adapters);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setTesting(false);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
              Government Verification Center
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Resilience layer with Circuit Breakers, Rate Limiters, Caching, and Retries across 10 Government Adapters.
            </p>
          </div>

          <button
            onClick={handleTestAdapters}
            disabled={testing}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-lg hover:bg-blue-500 transition-all"
          >
            <RefreshCw className={`h-4 w-4 ${testing ? 'animate-spin' : ''}`} />
            <span>{testing ? 'Executing 10 Adapters...' : 'Ping All 10 Government Adapters'}</span>
          </button>
        </div>

        {/* 10 Provider Cards Grid */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {providers.map((p) => (
            <div key={p.name} className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-blue-400" />
                  <span className="font-mono font-bold text-white text-sm">{p.name}</span>
                </div>
                <StatusBadge status={p.status} size="sm" />
              </div>
              <p className="text-xs text-slate-400">{p.full}</p>
              <div className="grid grid-cols-3 gap-2 text-[10px] font-mono text-slate-400 bg-slate-950 p-2 rounded border border-slate-850">
                <div>
                  <span className="block text-slate-500">RATE LIMIT</span>
                  <span className="text-slate-200">{p.rateLimit || '60/min'}</span>
                </div>
                <div>
                  <span className="block text-slate-500">LATENCY</span>
                  <span className="text-emerald-400">{p.latency_ms ? `${p.latency_ms}ms` : 'LIVE'}</span>
                </div>
                <div>
                  <span className="block text-slate-500">CONTEXT</span>
                  <span className="text-blue-400">{p.authorization_context || 'MOCK_SANDBOX'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
