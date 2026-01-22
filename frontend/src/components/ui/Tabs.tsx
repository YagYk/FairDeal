import React, { createContext, useContext, useState } from 'react';
import { cn } from '../../lib/utils';

interface TabsContextType {
    value: string;
    onValueChange: (value: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export const Tabs = ({
    defaultValue,
    value: controlledValue,
    onValueChange,
    children,
    className,
}: {
    defaultValue?: string;
    value?: string;
    onValueChange?: (value: string) => void;
    children: React.ReactNode;
    className?: string;
}) => {
    const [activeTab, setActiveTab] = useState(defaultValue || '');
    const value = controlledValue !== undefined ? controlledValue : activeTab;

    const handleValueChange = (newValue: string) => {
        if (controlledValue === undefined) {
            setActiveTab(newValue);
        }
        onValueChange?.(newValue);
    };

    return (
        <TabsContext.Provider value={{ value, onValueChange: handleValueChange }}>
            <div className={cn('w-full', className)}>{children}</div>
        </TabsContext.Provider>
    );
};

export const TabsList = ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div
        className={cn(
            'inline-flex h-10 items-center justify-center rounded-lg bg-slate-100 p-1 text-slate-500',
            className
        )}
    >
        {children}
    </div>
);

export const TabsTrigger = ({
    value,
    children,
    className,
}: {
    value: string;
    children: React.ReactNode;
    className?: string;
}) => {
    const context = useContext(TabsContext);
    const isActive = context?.value === value;

    return (
        <button
            onClick={() => context?.onValueChange(value)}
            className={cn(
                'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:pointer-events-none disabled:opacity-50',
                isActive ? 'bg-white text-slate-900 shadow-sm' : 'hover:bg-white/50 hover:text-slate-700',
                className
            )}
        >
            {children}
        </button>
    );
};

export const TabsContent = ({
    value,
    children,
    className,
}: {
    value: string;
    children: React.ReactNode;
    className?: string;
}) => {
    const context = useContext(TabsContext);
    if (context?.value !== value) return null;

    return <div className={cn('mt-2 focus-visible:outline-none', className)}>{children}</div>;
};
