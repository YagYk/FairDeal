import React from 'react';
import { cn } from '../../lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    error?: string;
    label?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, error, label, ...props }, ref) => {
        return (
            <div className="flex w-full flex-col space-y-1.5">
                {label && (
                    <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                        {label}
                    </label>
                )}
                <input
                    ref={ref}
                    className={cn(
                        'flex h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition-all placeholder:text-slate-600 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gold/30 disabled:cursor-not-allowed disabled:opacity-50',
                        error && 'border-red-500 focus-visible:ring-red-500',
                        className
                    )}
                    {...props}
                />
                {error && <p className="text-xs text-red-500">{error}</p>}
            </div>
        );
    }
);

Input.displayName = 'Input';
