import React from 'react';
import { ClauseDriftResult } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Activity, ShieldCheck, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';
import { cn, formatPercent } from '../../lib/utils';

interface ClauseDriftPanelProps {
    drifts: ClauseDriftResult[];
}

export const ClauseDriftPanel = ({ drifts }: ClauseDriftPanelProps) => {
    return (
        <Card className="shadow-premium border-none ring-1 ring-slate-200">
            <CardHeader className="border-b">
                <CardTitle className="flex items-center space-x-2">
                    <Activity className="h-5 w-5 text-brand-500" />
                    <span>Clause Drift / Alignment</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="divide-y divide-slate-100">
                    {drifts.map((drift, idx) => (
                        <DriftItem key={idx} drift={drift} />
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};

const DriftItem = ({ drift }: { drift: ClauseDriftResult }) => {
    const [expanded, setExpanded] = React.useState(false);
    const isAnomalous = drift.status === 'anomalous';

    return (
        <div className="p-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <Badge variant="secondary" className="uppercase tracking-widest px-1.5 h-5 text-[10px]">
                        {drift.clause_type}
                    </Badge>
                    <div className="flex items-center space-x-1.5">
                        {isAnomalous ? (
                            <ShieldAlert className="h-4 w-4 text-red-500" />
                        ) : (
                            <ShieldCheck className="h-4 w-4 text-emerald-500" />
                        )}
                        <span className={cn("text-xs font-bold uppercase tracking-tight", isAnomalous ? "text-red-600" : "text-emerald-600")}>
                            {drift.status}
                        </span>
                    </div>
                </div>
                <div className="flex items-center space-x-4">
                    <div className="text-right">
                        <span className="text-[10px] font-bold text-slate-400 uppercase block">Alignment</span>
                        <span className="text-sm font-bold text-slate-900">{formatPercent(drift.similarity_to_gold * 100)}</span>
                    </div>
                    <button
                        onClick={() => setExpanded(!expanded)}
                        className="rounded-full h-8 w-8 flex items-center justify-center hover:bg-slate-100 transition-colors text-slate-400"
                    >
                        {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                </div>
            </div>

            {expanded && (
                <div className="mt-4 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
                    <div className="rounded-xl border border-emerald-100 bg-emerald-50/30 p-4">
                        <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest block mb-1">Matched Gold Standard</span>
                        <p className="text-xs text-slate-700 leading-relaxed italic">
                            "{drift.matched_gold_clause_preview}..."
                        </p>
                    </div>

                    {drift.retrieved_examples.length > 0 && (
                        <div>
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-2">KB Reference Examples</span>
                            <div className="space-y-2">
                                {drift.retrieved_examples.map((ex, i) => (
                                    <div key={i} className="rounded-lg border border-slate-100 bg-white p-3 text-[11px] text-slate-600">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="font-bold text-slate-400">Match {formatPercent(ex.similarity * 100)}</span>
                                        </div>
                                        "{ex.text_preview}..."
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
