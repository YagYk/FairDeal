import React from 'react';
import { cn } from '../../lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg' | 'icon';
    loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', loading, children, ...props }, ref) => {
        const variants = {
            primary: 'bg-brand-500 text-white hover:bg-brand-600 shadow-sm active:scale-[0.98]',
            secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200 active:scale-[0.98]',
            outline: 'bg-transparent border border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-900',
            ghost: 'bg-transparent text-slate-500 hover:bg-slate-100 hover:text-slate-900',
            danger: 'bg-red-500 text-white hover:bg-red-600 shadow-sm active:scale-[0.98]',
        };

        const sizes = {
            sm: 'h-8 px-3 text-xs',
            md: 'h-10 px-4 text-sm',
            lg: 'h-12 px-6 text-base',
            icon: 'h-10 w-10 p-0 flex items-center justify-center',
        };

        return (
            <button
                ref={ref}
                className={cn(
                    'inline-flex items-center justify-center rounded-lg font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:pointer-events-none disabled:opacity-50',
                    variants[variant],
                    sizes[size],
                    className
                )}
                disabled={loading || props.disabled}
                {...props}
            >
                {loading ? (
                    <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                ) : null}
                {children}
            </button>
        );
    }
);

Button.displayName = 'Button';
