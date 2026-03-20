import React from 'react';
import { ScoreResult, ContractMetadata } from '../../lib/types';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';
import { ShieldCheck, TrendingUp, AlertCircle, Sparkles, Download, Copy } from 'lucide-react';
import { Button } from '../ui/Button';
import { cn } from '../../lib/utils';

interface ResultHeaderProps {
    scoring: ScoreResult;
    metadata?: ContractMetadata;
    cacheHit?: boolean;
    warnings?: string[];
    onDownloadJson: () => void;
    onCopySummary: () => void;
}

export const ResultHeader = ({
    scoring,
    metadata,
    cacheHit,
    warnings = [],
    onDownloadJson,
    onCopySummary
}: ResultHeaderProps) => {
    const getScoreLabel = (score: number) => {
        if (score >= 80) return { label: 'Excellent', color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' };
        if (score >= 60) return { label: 'Good', color: 'text-gold', bg: 'bg-gold/10 border-gold/20' };
        if (score >= 40) return { label: 'Average', color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' };
        return { label: 'Risky', color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' };
    };

    const scoreInfo = getScoreLabel(scoring.overall_score);

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center space-x-3 mb-2">
                        <h1 className="text-3xl font-serif font-bold text-white tracking-tight">Analysis Report</h1>
                        {cacheHit && (
                            <Badge variant="secondary" className="font-mono text-[10px] h-5">
                                <Sparkles className="h-3 w-3 mr-1" />
                                CACHE HIT
                            </Badge>
                        )}
                        {warnings.length > 0 && (
                            <Badge variant="warning" className="text-[10px] h-5">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                {warnings.length} WARNINGS
                            </Badge>
                        )}
                    </div>
                    {(metadata?.role_title || metadata?.company_name) ? (
                        <div className="flex items-center space-x-2 text-slate-400 text-sm font-medium mb-1">
                            {metadata?.role_title && (
                                <span className="bg-white/5 px-2 py-0.5 rounded text-slate-300 border border-white/10">
                                    {metadata.role_title}
                                </span>
                            )}
                            {metadata?.company_name && (
                                <>
                                    <span className="text-slate-600">•</span>
                                    <span>{metadata.company_name}</span>
                                </>
                            )}
                        </div>
                    ) : (
                        <p className="text-slate-500">Deterministic audit based on Knowledge Base analysis and market standards.</p>
                    )}
                </div>

                <div className="flex items-center space-x-3">
                    <Button variant="outline" size="sm" onClick={onCopySummary}>
                        <Copy className="h-4 w-4 mr-2" />
                        Copy Summary
                    </Button>
                    <Button variant="primary" size="sm" onClick={onDownloadJson}>
                        <Download className="h-4 w-4 mr-2" />
                        JSON Report
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="md:col-span-2 p-6 border-white/5 bg-white/5 backdrop-blur-xl flex items-center justify-between">
                    <div className="space-y-1">
                        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Overall Score</span>
                        <div className="flex items-baseline space-x-2">
                            <span className="text-5xl font-black text-white">{Math.round(scoring.overall_score)}</span>
                            <span className="text-xl font-bold text-slate-500">/ 100</span>
                        </div>
                        <div className={cn("inline-flex items-center rounded-full px-2 py-0.5 text-xs font-bold border mt-2", scoreInfo.bg, scoreInfo.color)}>
                            {scoreInfo.label}
                        </div>
                    </div>

                    <div className="hidden sm:block">
                        <div className="relative h-24 w-24">
                            <svg className="h-full w-full" viewBox="0 0 100 100">
                                <circle className="text-white/5" strokeWidth="10" stroke="currentColor" fill="transparent" r="40" cx="50" cy="50" />
                                <circle
                                    className={cn("transition-all duration-1000 ease-out", scoreInfo.color)}
                                    strokeWidth="10" strokeDasharray="251.2" strokeDashoffset={251.2 - (scoring.overall_score / 100) * 251.2}
                                    strokeLinecap="round" stroke="currentColor" fill="transparent" r="40" cx="50" cy="50" transform="rotate(-90 50 50)"
                                />
                            </svg>
                        </div>
                    </div>
                </Card>

                <Card className="p-6 border-white/5 bg-white/5 backdrop-blur-xl flex flex-col justify-center">
                    <div className="flex items-center space-x-2 mb-2">
                        <ShieldCheck className="h-4 w-4 text-emerald-400" />
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Safety Score</span>
                    </div>
                    <span className="text-3xl font-bold text-white">{Math.round(scoring.safety_score)}</span>
                    <div className="mt-2 h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500/50 rounded-full" style={{ width: `${scoring.safety_score}%` }} />
                    </div>
                </Card>

                <Card className="p-6 border-white/5 bg-white/5 backdrop-blur-xl flex flex-col justify-center">
                    <div className="flex items-center space-x-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-gold" />
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Market Fairness</span>
                    </div>
                    <span className="text-3xl font-bold text-white">{Math.round(scoring.market_fairness_score)}</span>
                    <div className="mt-2 h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-gold/50 rounded-full" style={{ width: `${scoring.market_fairness_score}%` }} />
                    </div>
                </Card>
            </div>
        </div>
    );
};
