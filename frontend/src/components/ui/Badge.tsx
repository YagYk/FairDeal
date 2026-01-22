import React from 'react';
import { cn } from '../../lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning' | 'error' | 'info';
}

export const Badge = ({ className, variant = 'default', ...props }: BadgeProps) => {
    const variants = {
        default: 'bg-gold text-charcoal',
        secondary: 'bg-white/10 text-slate-300 border border-white/5',
        outline: 'border border-gold/30 text-gold bg-gold/5',
        success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
        warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
        error: 'bg-red-500/10 text-red-400 border border-red-500/20',
        info: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
    };

    return (
        <div
            className={cn(
                'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500',
                variants[variant],
                className
            )}
            {...props}
        />
    );
};
