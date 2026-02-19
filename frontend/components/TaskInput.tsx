'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Send, Sparkles } from 'lucide-react';

export function TaskInput({
    onSubmit,
    isLoading = false,
}: {
    onSubmit: (prompt: string) => void;
    isLoading?: boolean;
}) {
    const [prompt, setPrompt] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim() || isLoading) return;
        onSubmit(prompt.trim());
        setPrompt('');
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
            <div className="relative group">
                <div className="absolute -inset-0.5 rounded-xl bg-gradient-to-r from-primary/50 via-purple-500/30 to-accent/50 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity duration-500 blur-sm" />
                <div className="relative flex items-center gap-2 rounded-xl border border-border bg-card/80 backdrop-blur-sm p-2 shadow-lg">
                    <Sparkles className="w-5 h-5 text-primary ml-2 animate-glow-pulse" />
                    <input
                        type="text"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Describe your task… (e.g., 'Build a React todo app with dark mode')"
                        className="flex-1 bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground px-2"
                        disabled={isLoading}
                        id="task-input"
                    />
                    <Button
                        type="submit"
                        size="sm"
                        disabled={!prompt.trim() || isLoading}
                        className="gap-1.5"
                    >
                        <Send className="w-3.5 h-3.5" />
                        {isLoading ? 'Running…' : 'Execute'}
                    </Button>
                </div>
            </div>
        </form>
    );
}
