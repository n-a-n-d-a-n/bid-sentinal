'use client';

import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { CytoscapeGraphData } from '@/lib/api/types';
import { Network, ShieldAlert, CheckCircle, Info } from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';

interface CytoscapeGraphProps {
  data: CytoscapeGraphData;
  height?: string;
}

export const CytoscapeGraph: React.FC<CytoscapeGraphProps> = ({ data, height = '500px' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [...data.nodes, ...data.edges],
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#f8fafc',
            'font-size': '10px',
            'font-family': 'Google Sans, sans-serif',
            'text-valign': 'bottom',
            'text-margin-y': 4,
            'background-color': '#3b82f6',
            'border-width': 2,
            'border-color': '#1d4ed8',
            'width': 30,
            'height': 30,
          },
        },
        {
          selector: 'node[type = "BIDDER"]',
          style: {
            'background-color': '#2563eb',
            'border-color': '#60a5fa',
            'shape': 'ellipse',
            'width': 36,
            'height': 36,
          },
        },
        {
          selector: 'node[type = "DIRECTOR"]',
          style: {
            'background-color': '#d97706',
            'border-color': '#fbbf24',
            'shape': 'diamond',
          },
        },
        {
          selector: 'node[type = "ADDRESS"]',
          style: {
            'background-color': '#0891b2',
            'border-color': '#22d3ee',
            'shape': 'rectangle',
          },
        },
        {
          selector: 'node[type = "BANK_ACCOUNT"]',
          style: {
            'background-color': '#059669',
            'border-color': '#34d399',
            'shape': 'hexagon',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#334155',
            'target-arrow-color': '#334155',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(relationship)',
            'font-size': '8px',
            'color': '#94a3b8',
            'text-rotation': 'autorotate',
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: false,
        padding: 30,
      },
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      setSelectedNode(node.data());
    });

    const timer = setTimeout(() => {
      cy.resize();
      cy.fit(undefined, 40);
    }, 150);

    return () => {
      clearTimeout(timer);
      cy.destroy();
    };
  }, [data]);

  return (
    <div className="relative h-full w-full min-h-[550px] rounded-xl border border-slate-800 bg-slate-950 overflow-hidden shadow-2xl">
      {/* Visual Canvas */}
      <div
        ref={containerRef}
        style={{ height: height === '100%' ? '100%' : height, minHeight: '550px' }}
        className="w-full h-full bg-slate-950"
      />

      {/* Graph Controls Overlay */}
      <div className="absolute top-3 left-3 rounded-lg border border-slate-800 bg-slate-900/90 p-2.5 backdrop-blur-md text-xs font-mono text-slate-300">
        <div className="flex items-center gap-2 mb-1 text-slate-100 font-bold">
          <Network className="h-4 w-4 text-blue-400" />
          <span>Procurement Entity Network</span>
        </div>
        <div className="flex items-center gap-3 text-[10px] text-slate-400">
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-blue-500"/> Bidder</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-amber-500"/> Director</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-cyan-500"/> Address</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-emerald-500"/> Bank</span>
        </div>
      </div>

      {/* Selected Node Inspector Drawer */}
      {selectedNode && (
        <div className="absolute bottom-3 right-3 w-80 rounded-xl border border-slate-800 bg-slate-900/95 p-4 shadow-xl backdrop-blur-md">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-bold uppercase text-slate-200">{selectedNode.type} Entity</span>
            <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-white text-xs font-mono">✕</button>
          </div>
          <div className="mt-2 space-y-1.5 text-xs">
            <div className="font-semibold font-mono text-white">{selectedNode.label}</div>
            <div className="text-[11px] text-slate-400">ID: {selectedNode.id}</div>
            <div className="mt-2 rounded bg-slate-950 p-2 border border-slate-800 text-[11px] text-amber-300 flex items-start gap-1.5">
              <Info className="h-3.5 w-3.5 flex-shrink-0 text-amber-400" />
              <span>Potential shared-control relationship detected. Requires officer investigation.</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
