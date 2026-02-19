'use client';

import type { AgentEvent } from '@/lib/types';
import { cn } from '@/lib/utils';

export function AgentPanel({
    events,
    status,
}: {
    events: AgentEvent[];
    status: string;
}) {
    const thoughts = events.filter((e) => e.type === 'thought');
    const toolCalls = events.filter((e) => e.type === 'tool_call');
    const errors = events.filter((e) => e.type === 'error');

    return (
        <div className="h-full flex flex-col glass rounded-xl">
            <div className="px-4 py-3 border-b border-night-700/50 flex items-center justify-between">
                <h3 className="text-xs uppercase tracking-wider text-night-400">Agent Activity</h3>
                <span className={cn(
                    'text-xs px-2 py-0.5 rounded-full',
                    status === 'running' ? 'bg-luxor-600/30 text-luxor-300' :
                        status === 'completed' ? 'bg-emerald-700/30 text-emerald-300' :
                            status === 'failed' ? 'bg-red-700/30 text-red-300' :
                                'bg-night-700/30 text-night-300'
                )}>
                    {status}
                </span>
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
                {events.length === 0 && (
                    <div className="text-center text-night-500 text-sm py-8">
                        Waiting for agent to start…
                    </div>
                )}
                {events.map((event, i) => (
                    <AgentEventItem key={i} event={event} />
                ))}
            </div>
        </div>
    );
}

function AgentEventItem({ event }: { event: AgentEvent }) {
    switch (event.type) {
        case 'thought':
            return (
                <div className="text-xs text-night-300 pl-3 border-l-2 border-night-700">
                    {event.content.text?.slice(0, 300)}
                </div>
            );
        case 'tool_call':
            return (
                <div className="glass rounded-lg p-2.5">
                    <span className="text-xs font-mono text-luxor-400">{event.content.tool}</span>
                    <pre className="text-[11px] text-night-400 font-mono mt-1 overflow-x-auto">
                        {JSON.stringify(event.content.arguments, null, 2)?.slice(0, 200)}
                    </pre>
                </div>
            );
        case 'tool_result':
            return (
                <div className={cn(
                    'text-xs font-mono p-2 rounded',
                    event.content.success ? 'bg-emerald-950/30 text-emerald-300' : 'bg-red-950/30 text-red-300'
                )}>
                    {event.content.output?.slice(0, 300)}
                </div>
            );
        case 'error':
            return (
                <div className="bg-red-950/30 border border-red-800/30 rounded p-2 text-xs text-red-300">
                    {event.content.error}
                </div>
            );
        default:
            return null;
    }
}
