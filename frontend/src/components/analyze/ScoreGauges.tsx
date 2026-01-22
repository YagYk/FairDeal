import React from 'react';
import { ScoreResult } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { cn } from '../../lib/utils';

interface ScoreGaugesProps {
    scoring: ScoreResult;
}

export const ScoreGauges = ({ scoring }: ScoreGaugesProps) => {
    return (
        <Card className="shadow-premium border-none ring-1 ring-slate-200">
            <CardHeader className="pb-2">
                <CardTitle className="text-sm">Analysis Scores</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="flex flex-col items-center">
                    <ScoreRing
                        score={scoring.overall_score}
                        size={120}
                        strokeWidth={10}
                        label="Overall"
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col items-center">
                        <ScoreRing
                            score={scoring.safety_score}
                            size={60}
                            strokeWidth={6}
                            label="Safety"
                            compact
                        />
                    </div>
                    <div className="flex flex-col items-center">
                        <ScoreRing
                            score={scoring.market_fairness_score}
                            size={60}
                            strokeWidth={6}
                            label="Market"
                            compact
                        />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

interface ScoreRingProps {
    score: number;
    size: number;
    strokeWidth: number;
    label: string;
    compact?: boolean;
}

const ScoreRing = ({ score, size, strokeWidth, label, compact }: ScoreRingProps) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (score / 100) * circumference;

    const getColor = (s: number) => {
        if (s >= 80) return 'text-emerald-500';
        if (s >= 60) return 'text-brand-500';
        if (s >= 40) return 'text-amber-500';
        return 'text-red-500';
    };

    return (
        <div className="relative inline-flex flex-col items-center">
            <svg width={size} height={size} className="rotate-[-90deg]">
                <circle
                    className="text-slate-100"
                    strokeWidth={strokeWidth}
                    stroke="currentColor"
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                />
                <circle
                    className={cn("transition-all duration-1000 ease-out", getColor(score))}
                    strokeWidth={strokeWidth}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                    r={radius}
                    cx={size / 2}
                    cy={size / 2}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={cn("font-bold text-slate-900", compact ? "text-sm" : "text-2xl")}>
                    {Math.round(score)}
                </span>
                {!compact && <span className="text-[10px] uppercase font-bold text-slate-400">/ 100</span>}
            </div>
            <span className={cn("mt-2 font-semibold text-slate-500", compact ? "text-[10px]" : "text-xs")}>
                {label}
            </span>
        </div>
    );
};
