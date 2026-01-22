import React from 'react';
import { cn } from '../../lib/utils';

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
    error?: string;
    label?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
    ({ className, error, label, children, ...props }, ref) => {
        return (
            <div className="flex w-full flex-col space-y-1.5">
                {label && (
                    <label className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                        {label}
                    </label>
                )}
                <div className="relative">
                    <select
                        ref={ref}
                        className={cn(
                            'flex h-10 w-full appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:cursor-not-allowed disabled:opacity-50',
                            error && 'border-red-500 focus-visible:ring-red-500',
                            className
                        )}
                        {...props}
                    >
                        {children}
                    </select>
                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                        <svg className="h-4 w-4 fill-current" viewBox="0 0 20 20">
                            <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" />
                        </svg>
                    </div>
                </div>
                {error && <p className="text-xs text-red-500">{error}</p>}
            </div>
        );
    }
);

Select.displayName = 'Select';
