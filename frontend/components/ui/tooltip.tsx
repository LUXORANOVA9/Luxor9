'use client';

import { cn } from '@/lib/utils';
import { useState, type ReactNode } from 'react';

function Tooltip({
    children,
    content,
    side = 'top',
}: {
    children: ReactNode;
    content: string;
    side?: 'top' | 'bottom' | 'left' | 'right';
}) {
    const [show, setShow] = useState(false);

    const positionClass = {
        top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
        bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
        left: 'right-full top-1/2 -translate-y-1/2 mr-2',
        right: 'left-full top-1/2 -translate-y-1/2 ml-2',
    }[side];

    return (
        <div
            className="relative inline-flex"
            onMouseEnter={() => setShow(true)}
            onMouseLeave={() => setShow(false)}
        >
            {children}
            {show && (
                <div
                    className={cn(
                        'absolute z-50 whitespace-nowrap rounded-md px-2.5 py-1',
                        'bg-foreground text-background text-xs font-medium',
                        'animate-fade-in pointer-events-none',
                        positionClass
                    )}
                >
                    {content}
                </div>
            )}
        </div>
    );
}

export { Tooltip };
