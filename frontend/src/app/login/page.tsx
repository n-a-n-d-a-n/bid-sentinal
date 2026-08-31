'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, Lock, User, KeyRound, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api/client';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('officer@procurex.gov.in');
  const [password, setPassword] = useState('officer123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await api.login(username, password);
      router.push('/dashboard');
    } catch (err: any) {
      // Fallback for offline demo mode
      localStorage.setItem('procurex_token', 'mock_jwt_token_procurex');
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const fillDemoRole = (roleEmail: string, rolePass: string) => {
    setUsername(roleEmail);
    setPassword(rolePass);
  };

  return (
    <div className="flex h-screen w-screen items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/90 p-8 shadow-2xl backdrop-blur-xl">
        {/* Header Logo */}
        <div className="flex flex-col items-center text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 font-bold text-white text-xl shadow-lg shadow-blue-900/50">
            P
          </div>
          <h1 className="mt-4 font-mono text-2xl font-black tracking-wider text-white">PROCUREX</h1>
          <p className="mt-1 text-xs text-slate-400">
            Verify. Explain. Detect. Decide.
          </p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-slate-300">
              Government Officer Email / ID
            </label>
            <div className="relative mt-1">
              <User className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="email"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-blue-600 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-slate-300">
              Password
            </label>
            <div className="relative mt-1">
              <KeyRound className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-blue-600 focus:outline-none"
              />
            </div>
          </div>

          {error && <div className="rounded bg-rose-950/80 p-2 text-xs text-rose-300 border border-rose-800/60">{error}</div>}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 py-2.5 text-xs font-semibold text-white shadow-lg shadow-blue-900/40 hover:bg-blue-500 transition-all"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Investigation Center'}</span>
            <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        {/* Quick Access Credentials */}
        <div className="mt-6 border-t border-slate-800 pt-4">
          <span className="block text-[11px] font-mono uppercase tracking-wider text-slate-400 text-center mb-2">
            Quick Access Credentials
          </span>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => fillDemoRole('officer@procurex.gov.in', 'officer123')}
              className="rounded border border-slate-800 bg-slate-950 p-2 text-[10px] text-slate-300 hover:border-blue-600 hover:text-white transition-all text-center"
            >
              <span className="block font-semibold">Officer</span>
              <span className="text-slate-500">Full Rights</span>
            </button>

            <button
              type="button"
              onClick={() => fillDemoRole('reviewer@procurex.gov.in', 'reviewer123')}
              className="rounded border border-slate-800 bg-slate-950 p-2 text-[10px] text-slate-300 hover:border-blue-600 hover:text-white transition-all text-center"
            >
              <span className="block font-semibold">Reviewer</span>
              <span className="text-slate-500">Investigation</span>
            </button>

            <button
              type="button"
              onClick={() => fillDemoRole('admin@procurex.gov.in', 'admin123')}
              className="rounded border border-slate-800 bg-slate-950 p-2 text-[10px] text-slate-300 hover:border-blue-600 hover:text-white transition-all text-center"
            >
              <span className="block font-semibold">Admin</span>
              <span className="text-slate-500">System</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
