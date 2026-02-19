'use client';

import { cn } from '@/lib/utils';
import { useRef, useEffect, type ReactNode } from 'react';

function ScrollArea({
    children,
    className,
    autoScroll = false,
}: {
    children: ReactNode;
    className?: string;
    autoScroll?: boolean;
}) {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (autoScroll && ref.current) {
            ref.current.scrollTop = ref.current.scrollHeight;
        }
    });

    return (
        <div
            ref={ref}
            className={cn('overflow-auto', className)}
        >
            {children}
        </div>
    );
}

export { ScrollArea };
