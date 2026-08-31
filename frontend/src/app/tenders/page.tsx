'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { FileCheck2, Filter, Search, RefreshCw, Plus, X } from 'lucide-react';
import { api, apiClient } from '@/lib/api/client';

export default function TendersPage() {
  const [tenders, setTenders] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    title: '',
    gem_bid_number: '',
    category: 'GOODS',
    estimated_value_inr: 10000000,
  });

  const fetchTenders = async () => {
    setLoading(true);
    try {
      const res: any = await api.getTenders();
      if (res?.items) {
        setTenders(res.items);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTenders();
  }, []);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await apiClient.post('/tenders', {
        title: form.title,
        gem_bid_number: form.gem_bid_number || `GEM/2026/B/${Math.floor(1000000 + Math.random() * 9000000)}`,
        category: form.category,
        estimated_value_inr: Number(form.estimated_value_inr),
      });
      setShowModal(false);
      setForm({ title: '', gem_bid_number: '', category: 'GOODS', estimated_value_inr: 10000000 });
      fetchTenders();
    } catch (err) {
      console.error(err);
    } finally {
      setCreating(false);
    }
  };

  const filtered = tenders.filter(t =>
    t.title?.toLowerCase().includes(search.toLowerCase()) ||
    t.gem_bid_number?.toLowerCase().includes(search.toLowerCase()) ||
    t.category?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
              Tender Requirement Intelligence
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              Extracted & normalized tender requirements across 17 canonical procurement types.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowModal(true)}
              className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-2 text-xs font-semibold text-white shadow-lg hover:bg-blue-500 transition-all font-sans"
            >
              <Plus className="h-4 w-4" />
              <span>Create New Tender</span>
            </button>
            <button
              onClick={fetchTenders}
              className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs font-mono text-slate-300 hover:bg-slate-850 transition-all"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Sync Live Tenders</span>
            </button>
          </div>
        </div>

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-mono text-sm font-bold text-white uppercase">Create GeM Procurement Tender</h3>
                <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                  <X className="h-4 w-4" />
                </button>
              </div>

              <form onSubmit={handleCreateSubmit} className="space-y-4 font-mono text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Tender Title</label>
                  <input
                    type="text"
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                    placeholder="e.g. Procurement of High-Capacity Transformers"
                    className="w-full rounded border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:outline-none"
                    required
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">GeM Bid Number (Optional)</label>
                  <input
                    type="text"
                    value={form.gem_bid_number}
                    onChange={(e) => setForm({ ...form, gem_bid_number: e.target.value })}
                    placeholder="GEM/2026/B/1049921"
                    className="w-full rounded border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:outline-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-slate-400 mb-1">Category</label>
                    <select
                      value={form.category}
                      onChange={(e) => setForm({ ...form, category: e.target.value })}
                      className="w-full rounded border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:outline-none"
                    >
                      <option value="GOODS">GOODS</option>
                      <option value="SERVICES">SERVICES</option>
                      <option value="WORKS">WORKS</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-slate-400 mb-1">Est. Value (INR)</label>
                    <input
                      type="number"
                      value={form.estimated_value_inr}
                      onChange={(e) => setForm({ ...form, estimated_value_inr: Number(e.target.value) })}
                      className="w-full rounded border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:outline-none"
                      required
                    />
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button type="button" onClick={() => setShowModal(false)} className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700">Cancel</button>
                  <button type="submit" disabled={creating} className="px-4 py-1.5 rounded bg-blue-600 text-white font-semibold hover:bg-blue-500 disabled:opacity-50">
                    {creating ? 'Registering Tender...' : 'Publish Tender'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl">
          <div className="flex items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter by tender ID, title, procurement category..."
                className="w-full rounded-lg border border-slate-800 bg-slate-950 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-blue-600 focus:outline-none"
              />
            </div>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 font-mono text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Tender Number</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Est. Value (INR)</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {filtered.length > 0 ? (
                  filtered.map((t) => (
                    <tr key={t.id} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-white">{t.gem_bid_number || t.id}</td>
                      <td className="py-3 px-4 font-medium text-slate-200">{t.title}</td>
                      <td className="py-3 px-4"><span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] font-mono">{t.category || 'GOODS'}</span></td>
                      <td className="py-3 px-4 font-mono text-emerald-400">₹{(t.estimated_value_inr || 10000000).toLocaleString('en-IN')}</td>
                      <td className="py-3 px-4"><StatusBadge status={t.status || 'PUBLISHED'} size="sm" /></td>
                      <td className="py-3 px-4 text-right">
                        <Link href={`/tenders/${t.id}`} className="text-blue-400 font-semibold hover:underline">
                          Requirements →
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center font-mono text-xs text-slate-400">
                      No active tenders published in database.
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
