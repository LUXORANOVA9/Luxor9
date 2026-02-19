'use client';

import { cn } from '@/lib/utils';
import { createContext, useContext, useState, type ReactNode } from 'react';

interface TabsContextValue {
    value: string;
    onChange: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue>({
    value: '',
    onChange: () => { },
});

function Tabs({
    defaultValue,
    value: controlledValue,
    onValueChange,
    children,
    className,
}: {
    defaultValue?: string;
    value?: string;
    onValueChange?: (value: string) => void;
    children: ReactNode;
    className?: string;
}) {
    const [internalValue, setInternalValue] = useState(defaultValue || '');
    const value = controlledValue ?? internalValue;
    const onChange = onValueChange ?? setInternalValue;

    return (
        <TabsContext.Provider value={{ value, onChange }}>
            <div className={cn('flex flex-col', className)}>{children}</div>
        </TabsContext.Provider>
    );
}

function TabsList({ children, className }: { children: ReactNode; className?: string }) {
    return (
        <div
            className={cn(
                'inline-flex items-center gap-1 rounded-lg bg-secondary/50 p-1',
                className
            )}
        >
            {children}
        </div>
    );
}

function TabsTrigger({
    value,
    children,
    className,
}: {
    value: string;
    children: ReactNode;
    className?: string;
}) {
    const ctx = useContext(TabsContext);
    const isActive = ctx.value === value;

    return (
        <button
            onClick={() => ctx.onChange(value)}
            className={cn(
                'inline-flex items-center justify-center rounded-md px-3 py-1.5 text-xs font-medium transition-all duration-200',
                isActive
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground hover:bg-background/50',
                className
            )}
        >
            {children}
        </button>
    );
}

function TabsContent({
    value,
    children,
    className,
}: {
    value: string;
    children: ReactNode;
    className?: string;
}) {
    const ctx = useContext(TabsContext);
    if (ctx.value !== value) return null;

    return (
        <div className={cn('mt-2 animate-fade-in', className)}>
            {children}
        </div>
    );
}

export { Tabs, TabsList, TabsTrigger, TabsContent };
