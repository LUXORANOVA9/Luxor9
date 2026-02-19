import { cn } from '@/lib/utils';
import { forwardRef, type ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'default' | 'secondary' | 'ghost' | 'destructive' | 'outline';
    size?: 'sm' | 'md' | 'lg' | 'icon';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'default', size = 'md', ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                    'disabled:pointer-events-none disabled:opacity-50',
                    'active:scale-[0.98]',
                    {
                        'bg-primary text-primary-foreground hover:bg-primary/90 shadow-md hover:shadow-lg glow-blue':
                            variant === 'default',
                        'bg-secondary text-secondary-foreground hover:bg-secondary/80':
                            variant === 'secondary',
                        'hover:bg-secondary/50 text-foreground': variant === 'ghost',
                        'bg-destructive text-destructive-foreground hover:bg-destructive/90':
                            variant === 'destructive',
                        'border border-border bg-transparent hover:bg-secondary/30':
                            variant === 'outline',
                    },
                    {
                        'h-8 px-3 text-xs': size === 'sm',
                        'h-10 px-4 text-sm': size === 'md',
                        'h-12 px-6 text-base': size === 'lg',
                        'h-9 w-9 p-0': size === 'icon',
                    },
                    className
                )}
                {...props}
            />
        );
    }
);
Button.displayName = 'Button';

export { Button };
export type { ButtonProps };
