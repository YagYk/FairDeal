import React from 'react';
import { ScoreResult } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Copy, Calculator } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ScoreBreakdownProps {
    scoring: ScoreResult;
}

/** Parse the weight from the reason string, e.g. "Salary Check: Scored 50/100 (Weight: 40%)" → 40 */
const parseWeight = (reason: string): number | null => {
    const m = reason.match(/Weight:\s*(\d+)%/i);
    return m ? parseInt(m[1], 10) : null;
};

/** Get a color class for a score value 0-100 */
const scoreColor = (score: number): string => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-amber-400';
    return 'text-red-400';
};

const barColor = (score: number): string => {
    if (score >= 80) return 'bg-emerald-400';
    if (score >= 60) return 'bg-amber-400';
    return 'bg-red-400';
};

export const ScoreBreakdown = ({ scoring }: ScoreBreakdownProps) => {
    const copyBreakdown = () => {
        const text = `FairDeal Score Breakdown:
Overall: ${scoring.overall_score.toFixed(0)}/100 (${scoring.grade})
Safety: ${scoring.safety_score.toFixed(0)}/100
Market: ${scoring.market_fairness_score.toFixed(0)}/100

Components:
${scoring.breakdown.map(b => {
            const w = parseWeight(b.reason);
            return `- ${b.factor}: ${b.points.toFixed(0)}/100${w ? ` (${w}% weight)` : ''}`;
        }).join('\n')}
`;
        navigator.clipboard.writeText(text);
    };

    return (
        <Card className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden">
            <CardHeader className="border-b border-white/5 bg-white/5 py-3 px-5">
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 mb-0">
                        <Calculator className="h-4 w-4 text-gold" />
                        <span>Score Audit</span>
                    </CardTitle>
                    <button
                        onClick={copyBreakdown}
                        className="flex items-center text-[10px] font-bold text-slate-500 hover:text-gold uppercase tracking-widest transition-colors"
                    >
                        <Copy className="h-3 w-3 mr-1.5" />
                        Copy
                    </button>
                </div>
            </CardHeader>
            <CardContent className="p-0">
                {/* Score Components */}
                <div className="p-5">
                    <div className="space-y-3.5">
                        {scoring.breakdown.length > 0 ? (
                            scoring.breakdown.map((item, idx) => {
                                const weight = parseWeight(item.reason);
                                const score = Math.round(item.points);

                                return (
                                    <div key={idx} className="space-y-1.5">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs font-bold text-white capitalize">
                                                    {item.factor.replace(/_/g, ' ')}
                                                </span>
                                                {weight && (
                                                    <span className="text-[9px] text-slate-600 font-mono">
                                                        {weight}% weight
                                                    </span>
                                                )}
                                            </div>
                                            <span className={cn('text-xs font-bold font-mono', scoreColor(score))}>
                                                {score}/100
                                            </span>
                                        </div>
                                        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                            <div
                                                className={cn('h-full rounded-full transition-all duration-1000', barColor(score))}
                                                style={{ width: `${Math.min(score, 100)}%` }}
                                            />
                                        </div>
                                    </div>
                                );
                            })
                        ) : (
                            <p className="text-xs text-slate-500 py-2">No breakdown data available.</p>
                        )}
                    </div>
                </div>

                {/* Risk Factors (if any) */}
                {scoring.risk_factors && scoring.risk_factors.length > 0 && (
                    <div className="px-4 pb-4">
                        <p className="text-[9px] text-slate-600 uppercase font-bold tracking-widest mb-2">Risk Factors</p>
                        <div className="space-y-1">
                            {scoring.risk_factors.map((rf, idx) => (
                                <div key={idx} className="flex items-center gap-2 text-[11px] text-red-400/80">
                                    <span className="h-1 w-1 rounded-full bg-red-400/60 shrink-0" />
                                    {rf}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Auxiliary Signals */}
                <div className="p-4 bg-white/[0.02] border-t border-white/5">
                    <div className="grid grid-cols-2 gap-3">
                        <AuxStat label="Safety" value={Math.round(scoring.safety_score)} />
                        <AuxStat label="Market Fairness" value={Math.round(scoring.market_fairness_score)} />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

const AuxStat = ({ label, value }: { label: string; value: number }) => (
    <div className="rounded-xl border border-white/5 bg-white/5 p-3">
        <span className="text-[9px] font-bold text-slate-500 uppercase block mb-0.5">{label}</span>
        <div className="flex items-baseline space-x-1">
            <span className={cn('text-lg font-bold', scoreColor(value))}>{value}</span>
            <span className="text-[9px] text-slate-600">/ 100</span>
        </div>
        <div className="mt-1.5 h-1 w-full bg-white/5 rounded-full overflow-hidden">
            <div className={cn('h-full rounded-full', barColor(value))} style={{ width: `${value}%` }} />
        </div>
    </div>
);
