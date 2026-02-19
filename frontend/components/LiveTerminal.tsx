'use client';

import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { ScrollArea } from './ui/scroll-area';
import { Terminal } from 'lucide-react';

export function LiveTerminal({ outputs }: { outputs: string[] }) {
    return (
        <Card className="h-full flex flex-col">
            <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-xs">
                    <Terminal className="w-3.5 h-3.5 text-green-400" />
                    <span>Terminal Output</span>
                    <div className="flex gap-1.5 ml-auto">
                        <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                        <div className="w-2.5 h-2.5 rounded-full bg-amber-500/60" />
                        <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
                    </div>
                </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-0">
                <ScrollArea className="h-full terminal-bg rounded-b-xl p-4" autoScroll>
                    {outputs.length === 0 ? (
                        <div className="text-muted-foreground text-xs font-mono">
                            <span className="text-green-400">luxor9</span>
                            <span className="text-muted-foreground">:</span>
                            <span className="text-blue-400">~</span>
                            <span className="text-muted-foreground">$ </span>
                            <span className="animate-glow-pulse">▌</span>
                        </div>
                    ) : (
                        <div className="space-y-1">
                            {outputs.map((line, i) => (
                                <pre
                                    key={i}
                                    className="text-xs font-mono text-foreground/80 whitespace-pre-wrap break-all animate-fade-in"
                                >
                                    {line}
                                </pre>
                            ))}
                        </div>
                    )}
                </ScrollArea>
            </CardContent>
        </Card>
    );
}
