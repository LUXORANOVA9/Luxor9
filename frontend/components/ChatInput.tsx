'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Send } from 'lucide-react';

export function ChatInput({
    onSend,
    disabled = false,
}: {
    onSend: (message: string) => void;
    disabled?: boolean;
}) {
    const [message, setMessage] = useState('');

    const handleSend = () => {
        if (!message.trim() || disabled) return;
        onSend(message.trim());
        setMessage('');
    };

    return (
        <div className="flex items-center gap-2 border-t border-border p-3 bg-card/50">
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Send a follow-up instruction…"
                className="flex-1 bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground"
                disabled={disabled}
                id="chat-input"
            />
            <Button
                size="icon"
                variant="ghost"
                onClick={handleSend}
                disabled={!message.trim() || disabled}
            >
                <Send className="w-4 h-4" />
            </Button>
        </div>
    );
}
