import React, { useState } from 'react';
import { cn } from '../../lib/utils';

interface TooltipProps {
    content: string;
    children: React.ReactNode;
    className?: string;
}

export const Tooltip = ({ content, children, className }: TooltipProps) => {
    const [isVisible, setIsVisible] = useState(false);

    return (
        <div
            className="relative flex items-center"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
        >
            {children}
            {isVisible && (
                <div
                    className={cn(
                        'absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 transform rounded bg-slate-900 px-2 py-1 text-xs text-white shadow-lg animate-in fade-in zoom-in duration-200',
                        className
                    )}
                >
                    {content}
                    <div className="absolute top-full left-1/2 -mt-1 -translate-x-1/2 border-4 border-transparent border-t-slate-900" />
                </div>
            )}
        </div>
    );
};
