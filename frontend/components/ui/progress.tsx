import { cn } from '@/lib/utils';

function Progress({
    value = 0,
    max = 100,
    className,
    variant = 'default',
}: {
    value?: number;
    max?: number;
    className?: string;
    variant?: 'default' | 'success' | 'warning';
}) {
    const percentage = Math.min(100, Math.max(0, (value / max) * 100));

    return (
        <div
            className={cn(
                'relative h-2 w-full overflow-hidden rounded-full bg-secondary/50',
                className
            )}
        >
            <div
                className={cn(
                    'h-full rounded-full transition-all duration-500 ease-out',
                    {
                        'bg-primary': variant === 'default',
                        'bg-green-500': variant === 'success',
                        'bg-amber-500': variant === 'warning',
                    }
                )}
                style={{ width: `${percentage}%` }}
            />
        </div>
    );
}

export { Progress };
