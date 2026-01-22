import React from 'react';
import { ScoreResult } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Copy, Calculator, ChevronDown } from 'lucide-react';
import { Button } from '../ui/Button';

interface ScoreBreakdownProps {
    scoring: ScoreResult;
}

export const ScoreBreakdown = ({ scoring }: ScoreBreakdownProps) => {
    const copyBreakdown = () => {
        const text = `FairDeal Score Breakdown:
Overall Score: ${scoring.overall_score.toFixed(0)}
Grade: ${scoring.grade}
Formula: ${scoring.score_formula}
Safety Score: ${scoring.safety_score.toFixed(0)}
Market Score: ${scoring.market_fairness_score.toFixed(0)}

Breakdown:
${scoring.breakdown.map(b => `- ${b.factor}: ${b.points > 0 ? '+' : ''}${b.points.toFixed(1)} (${b.reason})`).join('\n')}
`;
        navigator.clipboard.writeText(text);
    };

    return (
        <Card className="shadow-premium border-none ring-1 ring-slate-200 overflow-hidden">
            <CardHeader className="border-b bg-slate-50/50">
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center space-x-2">
                        <Calculator className="h-5 w-5 text-brand-500" />
                        <span>Audit Breakdown</span>
                    </CardTitle>
                    <Button variant="ghost" size="sm" onClick={copyBreakdown} className="text-slate-500">
                        <Copy className="h-4 w-4 mr-2" />
                        Copy Audit
                    </Button>
                </div>
            </CardHeader>
            <CardContent className="p-0">
                <div className="p-6 border-b border-slate-100 bg-slate-900 text-slate-300 font-mono text-[10px] leading-relaxed relative">
                    <Badge variant="outline" className="absolute top-4 right-4 text-slate-500 border-slate-700 bg-slate-800 uppercase tracking-widest px-1.5 h-4">
                        Deterministic Formula
                    </Badge>
                    <p className="text-slate-500 mb-1">// CORE_SCORING_LOGIC</p>
                    <p className="text-brand-400">{scoring.score_formula}</p>
                </div>

                <div className="divide-y divide-slate-100">
                    <div className="p-6">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Score Components</h4>
                        <div className="space-y-4">
                            {scoring.breakdown.length > 0 ? (
                                scoring.breakdown.map((item, idx) => (
                                    <div key={idx} className="flex items-start justify-between gap-4">
                                        <div className="space-y-1">
                                            <div className="flex items-center space-x-2">
                                                <span className="text-sm font-bold text-slate-800">{item.factor.replace(/_/g, ' ')}</span>
                                                <Badge
                                                    variant={item.points >= 0 ? 'success' : 'error'}
                                                    className="h-4 text-[9px] uppercase"
                                                >
                                                    {item.points >= 0 ? '+' : ''}{item.points.toFixed(1)}
                                                </Badge>
                                            </div>
                                            <p className="text-xs text-slate-500 italic">"{item.reason}"</p>
                                            {item.source_text && (
                                                <p className="text-xs text-slate-400 truncate">Source: "{item.source_text}"</p>
                                            )}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-sm text-slate-500 py-2">No breakdown items available.</p>
                            )}
                        </div>
                    </div>

                    <div className="p-6 bg-slate-50/30">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Auxiliary Signals (Legacy)</h4>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="rounded-xl border border-slate-200 bg-white p-4">
                                <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Safety Score</span>
                                <div className="flex items-baseline space-x-1">
                                    <span className="text-xl font-bold text-slate-900">{Math.round(scoring.safety_score)}</span>
                                    <span className="text-[10px] text-slate-400">/ 100</span>
                                </div>
                                <div className="mt-2 h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-slate-900 opacity-20" style={{ width: `${scoring.safety_score}%` }} />
                                </div>
                            </div>
                            <div className="rounded-xl border border-slate-200 bg-white p-4">
                                <span className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Market Fairness</span>
                                <div className="flex items-baseline space-x-1">
                                    <span className="text-xl font-bold text-slate-900">{Math.round(scoring.market_fairness_score)}</span>
                                    <span className="text-[10px] text-slate-400">/ 100</span>
                                </div>
                                <div className="mt-2 h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                                    <div className="h-full bg-slate-900 opacity-20" style={{ width: `${scoring.market_fairness_score}%` }} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
