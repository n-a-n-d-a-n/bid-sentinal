import React from 'react';
import { clsx } from 'clsx';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || 'UNKNOWN').toUpperCase();

  let colorClasses = 'bg-slate-800 text-slate-300 border-slate-700';
  
  if (['PASS', 'VERIFIED', 'APPROVED', 'VALID', 'READY_FOR_REVIEW', 'CLEAN', 'COMPLETED', 'GROUNDED', 'READY'].includes(norm)) {
    colorClasses = 'bg-emerald-950/80 text-emerald-400 border-emerald-800/60 shadow-sm shadow-emerald-950';
  } else if (['MANUAL_REVIEW_REQUIRED', 'REVIEW', 'UNDER_REVIEW', 'WARNING', 'STALE', 'PARTIALLY_GROUNDED', 'CLARIFICATION_REQUIRED'].includes(norm)) {
    colorClasses = 'bg-amber-950/80 text-amber-400 border-amber-800/60 shadow-sm shadow-amber-950';
  } else if (['FAIL', 'REJECTED', 'BLOCKED', 'INVALID', 'MISMATCH', 'CRITICAL', 'CONFLICT', 'HIGH'].includes(norm)) {
    colorClasses = 'bg-rose-950/80 text-rose-400 border-rose-800/60 shadow-sm shadow-rose-950';
  } else if (['UNAVAILABLE', 'INCOMPLETE', 'MISSING_DOCUMENT', 'INSUFFICIENT_EVIDENCE'].includes(norm)) {
    colorClasses = 'bg-slate-900 text-slate-400 border-slate-700/80';
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs font-medium',
    lg: 'px-3 py-1.5 text-sm font-medium',
  }[size];

  return (
    <span className={clsx('inline-flex items-center gap-1.5 rounded-full border tracking-wide uppercase font-mono', colorClasses, sizeClasses)}>
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-75 animate-pulse" />
      {norm.replace(/_/g, ' ')}
    </span>
  );
};
