import React from 'react';
import { BookOpen } from 'lucide-react';
import { PolicyCitation } from '@/lib/api/types';

interface CitationBadgeProps {
  citation: PolicyCitation;
  onClick?: () => void;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({ citation, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-md border border-blue-800/60 bg-blue-950/60 px-2.5 py-1 text-xs font-mono text-blue-300 hover:bg-blue-900/80 hover:border-blue-700 transition-all shadow-sm"
    >
      <BookOpen className="h-3.5 w-3.5 text-blue-400" />
      <span>
        [{citation.source} | {citation.section} | Pg {citation.page}]
      </span>
    </button>
  );
};
