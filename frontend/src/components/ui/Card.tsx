import React from 'react';
import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    glass?: boolean;
}

export const Card = ({ className, glass, ...props }: CardProps) => {
    return (
        <div
            className={cn(
                'rounded-3xl border transition-all duration-300',
                glass ? 'liquid-glass' : 'border-white/5 bg-white/5 backdrop-blur-md',
                className
            )}
            {...props}
        />
    );
};

export const CardHeader = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
    <div className={cn('flex flex-col space-y-1.5 p-6', className)} {...props} />
);

export const CardTitle = ({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h3 className={cn('text-lg font-bold leading-none tracking-tight text-white mb-1', className)} {...props} />
);

export const CardDescription = ({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p className={cn('text-sm text-slate-500', className)} {...props} />
);

export const CardContent = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
    <div className={cn('p-6 pt-0', className)} {...props} />
);

export const CardFooter = ({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
    <div className={cn('flex items-center p-6 pt-0', className)} {...props} />
);
