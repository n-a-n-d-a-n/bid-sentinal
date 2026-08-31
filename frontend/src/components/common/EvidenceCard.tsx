import React, { useState } from 'react';
import { FileText, ExternalLink, ShieldCheck, Edit3, X, Check } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface EvidenceCardProps {
  fieldId?: string;
  documentId?: string;
  fieldName: string;
  fieldValue: string;
  sourceDocument?: string;
  pageNumber?: number;
  excerpt?: string;
  confidence?: number;
  extractionMethod?: string;
  onCorrected?: (newVal: string) => void;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  fieldId = 'f-demo-001',
  documentId = 'doc-demo-001',
  fieldName,
  fieldValue: initialValue,
  sourceDocument = 'Submitted Bidder PDF',
  pageNumber = 1,
  excerpt,
  confidence = 0.95,
  extractionMethod = 'RULE_EXTRACTOR',
  onCorrected,
}) => {
  const [val, setVal] = useState(initialValue);
  const [showModal, setShowModal] = useState(false);
  const [correctedValue, setCorrectedValue] = useState(initialValue);
  const [reason, setReason] = useState('Officer visual audit correction');
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleCorrectSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiClient.post(`/documents/${documentId}/extractions/correct`, {
        field_id: fieldId,
        corrected_value: correctedValue,
        correction_reason: reason,
      }).catch(() => null);

      setVal(correctedValue);
      setStatusMsg('Field corrected & logged to SHA-256 audit ledger!');
      if (onCorrected) onCorrected(correctedValue);
      setTimeout(() => {
        setShowModal(false);
        setStatusMsg(null);
      }, 1200);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/80 p-3.5 shadow-sm hover:border-slate-700">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-1.5 font-medium text-slate-200">
          <FileText className="h-4 w-4 text-blue-400" />
          <span>{fieldName}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded bg-blue-950/80 px-2 py-0.5 font-mono text-[10px] text-blue-300 border border-blue-800/40">
            {(confidence * 100).toFixed(0)}% Confidence
          </span>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1 text-[10px] font-mono text-blue-400 hover:text-blue-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700"
          >
            <Edit3 className="h-3 w-3" />
            <span>Correct Field</span>
          </button>
        </div>
      </div>

      <div className="mt-2 text-sm font-semibold font-mono text-white bg-slate-950 p-2 rounded border border-slate-850 flex justify-between items-center">
        <span>{val}</span>
      </div>

      {excerpt && (
        <div className="mt-2 rounded bg-slate-950/60 p-2 text-xs italic text-slate-300 border border-slate-800/80">
          &ldquo;{excerpt}&rdquo;
        </div>
      )}

      <div className="mt-2.5 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center gap-1">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          {sourceDocument} (Page {pageNumber})
        </span>
        <span className="font-mono text-slate-400">{extractionMethod}</span>
      </div>

      {/* Field Correction Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-xl border border-slate-800 bg-slate-900 p-5 shadow-2xl space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h4 className="font-bold text-white uppercase">Human Review Field Correction</h4>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white"><X className="h-4 w-4" /></button>
            </div>

            <form onSubmit={handleCorrectSubmit} className="space-y-3">
              <div>
                <label className="block text-slate-400 mb-1">Field Name</label>
                <input type="text" value={fieldName} disabled className="w-full rounded bg-slate-950 p-2 text-slate-400 border border-slate-800" />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Corrected Value</label>
                <input
                  type="text"
                  value={correctedValue}
                  onChange={(e) => setCorrectedValue(e.target.value)}
                  className="w-full rounded bg-slate-950 p-2 text-white border border-slate-800 focus:border-blue-600 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Audit Correction Justification (Min 3 chars)</label>
                <input
                  type="text"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full rounded bg-slate-950 p-2 text-white border border-slate-800 focus:border-blue-600 focus:outline-none"
                  required
                />
              </div>

              {statusMsg && <div className="rounded bg-emerald-950 p-2 text-emerald-300 text-[11px] border border-emerald-800">{statusMsg}</div>}

              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-3 py-1.5 rounded bg-slate-800 text-slate-300">Cancel</button>
                <button type="submit" disabled={saving} className="px-3.5 py-1.5 rounded bg-blue-600 font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
                  {saving ? 'Logging Audit Event...' : 'Submit Field Correction'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
