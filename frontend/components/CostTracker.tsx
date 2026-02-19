'use client';

import { cn } from '@/lib/utils';

export function CostTracker({
    tokens = 0,
    cost = 0,
    turns = 0,
}: {
    tokens?: number;
    cost?: number;
    turns?: number;
}) {
    const formatCost = (c: number) => c === 0 ? 'Free' : `$${c.toFixed(4)}`;

    return (
        <div className="glass rounded-xl p-3 flex items-center justify-between gap-4">
            <div className="flex items-center gap-1.5">
                <span className="text-luxor-400 text-xs">⚡</span>
                <span className="text-xs font-mono text-night-300">
                    {tokens.toLocaleString()} tokens
                </span>
            </div>
            <div className="flex items-center gap-1.5">
                <span className="text-emerald-400 text-xs">$</span>
                <span className="text-xs font-mono text-night-300">
                    {formatCost(cost)}
                </span>
            </div>
            <div className="flex items-center gap-1.5">
                <span className="text-blue-400 text-xs">↻</span>
                <span className="text-xs font-mono text-night-300">
                    {turns} turns
                </span>
            </div>
        </div>
    );
}
