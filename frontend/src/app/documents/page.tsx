'use client';

import React, { useState, useEffect } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { StatusBadge } from '@/components/common/StatusBadge';
import { FileText, Upload, CheckCircle2, ShieldCheck, X, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const res: any = await apiClient.get('/documents').catch(() => null);
      if (res && Array.isArray(res)) {
        setDocuments(res);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('entity_type', 'bid');
    formData.append('entity_id', 'demo-bid-001');

    try {
      const res: any = await apiClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadSuccess(`Document "${res.original_filename || file.name}" uploaded & SHA-256 verified!`);
      setFile(null);
      fetchDocuments();
      setTimeout(() => setShowModal(false), 1500);
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-mono text-2xl font-extrabold tracking-tight text-white">
              Document Intelligence & Evidence Security
            </h1>
            <p className="mt-1 text-xs text-slate-400">
              PyMuPDF parsing, OCR status, magic byte verification, and SHA-256 deduplication.
            </p>
          </div>

          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-lg hover:bg-blue-500 transition-all"
          >
            <Upload className="h-4 w-4" />
            <span>Upload Document</span>
          </button>
        </div>

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="font-mono text-sm font-bold text-white uppercase">Upload Verified Evidence PDF</h3>
                <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">
                  <X className="h-4 w-4" />
                </button>
              </div>

              <form onSubmit={handleUploadSubmit} className="space-y-4 font-mono text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Select Document File (.pdf, .png, .jpg)</label>
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                    className="w-full rounded border border-slate-800 bg-slate-950 p-2 text-slate-300 focus:outline-none"
                    required
                  />
                </div>

                {uploadError && <div className="rounded bg-rose-950/80 p-2 text-rose-300 text-[11px] border border-rose-800">{uploadError}</div>}
                {uploadSuccess && <div className="rounded bg-emerald-950/80 p-2 text-emerald-300 text-[11px] border border-emerald-800">{uploadSuccess}</div>}

                <div className="flex justify-end gap-2 pt-2">
                  <button type="button" onClick={() => setShowModal(false)} className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700">Cancel</button>
                  <button type="submit" disabled={uploading || !file} className="px-4 py-1.5 rounded bg-blue-600 text-white font-semibold hover:bg-blue-500 disabled:opacity-50">
                    {uploading ? 'Validating Magic Bytes...' : 'Upload & Register'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="font-mono text-sm font-bold text-slate-100 uppercase tracking-wider">
              Ingested Bidder Documents
            </h2>
            <button onClick={fetchDocuments} className="text-slate-400 hover:text-white text-xs flex items-center gap-1 font-mono">
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh List</span>
            </button>
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 font-mono">
              <thead className="bg-slate-950 text-[11px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Filename</th>
                  <th className="py-3 px-4">Classification</th>
                  <th className="py-3 px-4">OCR Status</th>
                  <th className="py-3 px-4">SHA-256 Checksum</th>
                  <th className="py-3 px-4 text-right">Security</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-850">
                {documents.length > 0 ? (
                  documents.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-3 px-4 font-semibold text-white flex items-center gap-2 font-sans">
                        <FileText className="h-4 w-4 text-blue-400" />
                        {d.original_filename || d.filename}
                      </td>
                      <td className="py-3 px-4"><span className="rounded bg-slate-800 px-2 py-0.5 text-[10px]">{d.document_type || 'FINANCIAL'}</span></td>
                      <td className="py-3 px-4"><StatusBadge status={d.ocr_status || 'COMPLETED'} size="sm" /></td>
                      <td className="py-3 px-4 text-slate-400 text-[10px] truncate max-w-[200px]">{d.sha256_hash}</td>
                      <td className="py-3 px-4 text-right text-emerald-400"><StatusBadge status={d.security_status || 'CLEAN'} size="sm" /></td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-8 text-center font-mono text-xs text-slate-400">
                      No ingested document evidence recorded in database. Upload a document to begin processing.
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
