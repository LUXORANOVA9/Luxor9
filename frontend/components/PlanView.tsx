'use client';

import { cn } from '@/lib/utils';

export function PlanView({ plan }: { plan: string | null }) {
    if (!plan) {
        return (
            <div className="glass rounded-xl p-6 text-center text-night-500 text-sm">
                Plan will appear here once generated…
            </div>
        );
    }

    return (
        <div className="glass rounded-xl p-4">
            <h3 className="text-xs font-semibold text-luxor-400 mb-3">Execution Plan</h3>
            <pre className="text-xs text-night-300 whitespace-pre-wrap font-mono leading-relaxed">
                {plan}
            </pre>
        </div>
    );
}
