import { cn } from '@/lib/utils';
import { type HTMLAttributes } from 'react';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
    variant?: 'default' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline';
}

function Badge({ className, variant = 'default', ...props }: BadgeProps) {
    return (
        <span
            className={cn(
                'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
                {
                    'bg-primary/20 text-primary border border-primary/30': variant === 'default',
                    'bg-secondary text-secondary-foreground': variant === 'secondary',
                    'bg-green-500/20 text-green-400 border border-green-500/30': variant === 'success',
                    'bg-amber-500/20 text-amber-400 border border-amber-500/30': variant === 'warning',
                    'bg-destructive/20 text-destructive border border-destructive/30': variant === 'destructive',
                    'border border-border text-muted-foreground': variant === 'outline',
                },
                className
            )}
            {...props}
        />
    );
}

export { Badge };
export type { BadgeProps };
