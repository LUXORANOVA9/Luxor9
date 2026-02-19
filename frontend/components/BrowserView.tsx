'use client';

import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Globe, ExternalLink } from 'lucide-react';

export function BrowserView({
    screenshot,
    url,
}: {
    screenshot?: string;
    url?: string;
}) {
    return (
        <Card className="h-full flex flex-col">
            <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-xs">
                    <Globe className="w-3.5 h-3.5 text-blue-400" />
                    Browser
                    {url && (
                        <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="ml-auto flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors"
                        >
                            <span className="truncate max-w-[200px]">{url}</span>
                            <ExternalLink className="w-3 h-3" />
                        </a>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-2">
                {screenshot ? (
                    <img
                        src={`data:image/png;base64,${screenshot}`}
                        alt="Browser screenshot"
                        className="w-full h-full object-contain rounded-lg border border-border"
                    />
                ) : (
                    <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
                        <div className="text-center">
                            <Globe className="w-10 h-10 mx-auto mb-2 opacity-20" />
                            <p>No browser activity yet</p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
