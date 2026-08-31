import React from 'react';
import { LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  variant?: 'blue' | 'emerald' | 'amber' | 'rose' | 'slate';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = 'slate',
}) => {
  const borderColors = {
    blue: 'border-blue-800/40 bg-blue-950/20 text-blue-400',
    emerald: 'border-emerald-800/40 bg-emerald-950/20 text-emerald-400',
    amber: 'border-amber-800/40 bg-amber-950/20 text-amber-400',
    rose: 'border-rose-800/40 bg-rose-950/20 text-rose-400',
    slate: 'border-slate-800 bg-slate-900/60 text-slate-400',
  }[variant];

  return (
    <div className={clsx('rounded-xl border p-4 shadow-lg backdrop-blur-sm transition-all hover:border-slate-700', borderColors)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</span>
        <div className="rounded-lg bg-slate-950/60 p-2 text-slate-200 border border-slate-800">
          <Icon className="h-5 w-5 text-current" />
        </div>
      </div>
      <div className="mt-3 flex items-baseline justify-between">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">{value}</span>
        {trend && <span className="text-xs font-mono text-emerald-400">{trend}</span>}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};
