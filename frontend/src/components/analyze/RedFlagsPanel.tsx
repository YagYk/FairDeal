import React, { useState } from 'react';
import { RedFlag, FavorableTerm, NegotiationPoint, Severity, NarrationResult } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import {
    ShieldAlert,
    AlertCircle,
    CheckCircle2,
    Lightbulb,
    MessageSquareQuote,
    Copy,
    ChevronDown,
    ChevronUp,
    Target,
    Sparkles,
    TrendingUp
} from 'lucide-react';
import { cn } from '../../lib/utils';

interface RedFlagsPanelProps {
    redFlags: RedFlag[];
    favorableTerms: FavorableTerm[];
    negotiationPoints: NegotiationPoint[];
    narration?: NarrationResult;
}

const severityConfig = {
    [Severity.CRITICAL]: { bg: 'bg-red-500/10', text: 'text-red-400', badge: 'error' as const, label: 'CRITICAL' },
    [Severity.HIGH]: { bg: 'bg-orange-500/10', text: 'text-orange-400', badge: 'warning' as const, label: 'HIGH' },
    [Severity.MEDIUM]: { bg: 'bg-amber-500/10', text: 'text-amber-400', badge: 'warning' as const, label: 'MEDIUM' },
    [Severity.LOW]: { bg: 'bg-white/5', text: 'text-slate-400', badge: 'secondary' as const, label: 'LOW' },
};

export const RedFlagsPanel = ({ redFlags, favorableTerms, negotiationPoints, narration }: RedFlagsPanelProps) => {
    const [expandedScript, setExpandedScript] = useState<string | null>(null);
    const [copiedId, setCopiedId] = useState<string | null>(null);

    const copyScript = (id: string, script: string) => {
        navigator.clipboard.writeText(script);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    return (
        <div className="space-y-6">
            {/* Red Flags Section */}
            {redFlags.length > 0 && (
                <Card className="border-red-500/20 bg-white/5 backdrop-blur-xl overflow-hidden">
                    <CardHeader className="bg-red-500/5 border-b border-red-500/10">
                        <CardTitle className="flex items-center space-x-2 text-red-400">
                            <ShieldAlert className="h-5 w-5" />
                            <span>Red Flags ({redFlags.length})</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 divide-y divide-white/5">
                        {redFlags.map((flag) => {
                            const config = severityConfig[flag.severity];
                            return (
                                <div key={flag.id} className="p-6">
                                    <div className="flex items-start space-x-4">
                                        <div className={cn("mt-1 flex h-10 w-10 items-center justify-center rounded-xl shrink-0", config.bg, config.text)}>
                                            <AlertCircle className="h-5 w-5" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center space-x-2 mb-2">
                                                <span className="text-sm font-bold text-white">{flag.rule}</span>
                                                <Badge variant={config.badge} className="h-5 text-[10px]">{config.label}</Badge>
                                                <span className="text-xs text-red-400 font-mono">{flag.impact_score} pts</span>
                                            </div>
                                            <p className="text-sm text-slate-400 mb-3">{flag.explanation}</p>

                                            {flag.market_context && (
                                                <div className="bg-white/5 rounded-lg p-3 mb-3 border border-white/5">
                                                    <p className="text-xs text-slate-500">
                                                        <span className="font-bold text-slate-400">Market Context:</span> {flag.market_context}
                                                    </p>
                                                </div>
                                            )}

                                            <div className="bg-gold/5 rounded-lg p-3 border border-gold/10">
                                                <div className="flex items-center space-x-1 mb-1">
                                                    <Lightbulb className="h-3 w-3 text-gold" />
                                                    <span className="text-xs font-bold text-gold uppercase">Recommendation</span>
                                                </div>
                                                <p className="text-xs text-slate-300">{flag.recommendation}</p>
                                            </div>

                                            {flag.source_text && (
                                                <p className="mt-3 text-xs text-slate-600 italic truncate">
                                                    Source: "{flag.source_text}"
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </CardContent>
                </Card>
            )}

            {/* Favorable Terms Section */}
            {favorableTerms.length > 0 && (
                <Card className="border-emerald-500/20 bg-white/5 backdrop-blur-xl overflow-hidden">
                    <CardHeader className="bg-emerald-500/5 border-b border-emerald-500/10">
                        <CardTitle className="flex items-center space-x-2 text-emerald-400">
                            <CheckCircle2 className="h-5 w-5" />
                            <span>Strong Points ({favorableTerms.length})</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 divide-y divide-white/5">
                        {favorableTerms.map((term) => (
                            <div key={term.id} className="p-6">
                                <div className="flex items-start space-x-4">
                                    <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 shrink-0">
                                        <TrendingUp className="h-5 w-5" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className="text-sm font-bold text-white">{term.term}</span>
                                            <Badge variant="success" className="h-5 text-[10px]">+{term.impact_score} pts</Badge>
                                        </div>
                                        <p className="text-sm text-slate-400 mb-2">{term.explanation}</p>
                                        <p className="text-xs font-mono text-emerald-400 bg-emerald-500/10 rounded px-2 py-1 inline-block border border-emerald-500/20">
                                            {term.value}
                                        </p>
                                        {term.market_context && (
                                            <p className="mt-2 text-xs text-slate-500">{term.market_context}</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </CardContent>
                </Card>
            )}

            {/* Negotiation Playbook */}
            {negotiationPoints.length > 0 && (
                <Card className="border-gold/10 bg-white/5 backdrop-blur-xl overflow-hidden">
                    <CardHeader className="bg-gold/5 border-b border-gold/10">
                        <CardTitle className="flex items-center space-x-2 text-gold">
                            <Target className="h-5 w-5" />
                            <span>Negotiation Playbook</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 divide-y divide-white/5">
                        {negotiationPoints.map((point) => (
                            <div key={point.id} className="p-6">
                                <div className="flex items-start space-x-4">
                                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gold/20 text-gold font-bold text-sm shrink-0 border border-gold/30">
                                        {point.priority}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm font-bold text-white">{point.topic}</span>
                                            <Badge variant="secondary" className="text-[10px]">{point.success_probability}</Badge>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4 mb-4">
                                            <div className="bg-red-500/5 rounded-lg p-3 border border-red-500/10">
                                                <p className="text-[10px] font-bold text-red-400 uppercase mb-1">Current</p>
                                                <p className="text-xs text-slate-300">{point.current_term}</p>
                                            </div>
                                            <div className="bg-emerald-500/5 rounded-lg p-3 border border-emerald-500/10">
                                                <p className="text-[10px] font-bold text-emerald-400 uppercase mb-1">Target</p>
                                                <p className="text-xs text-emerald-300">{point.target_term}</p>
                                            </div>
                                        </div>

                                        <p className="text-xs text-slate-400 mb-4">{point.rationale}</p>

                                        {/* Email Script */}
                                        <div className="bg-white/5 rounded-xl border border-white/5 overflow-hidden">
                                            <button
                                                onClick={() => setExpandedScript(expandedScript === point.id ? null : point.id)}
                                                className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
                                            >
                                                <span className="text-xs font-bold text-slate-400 uppercase tracking-wide flex items-center space-x-2">
                                                    <MessageSquareQuote className="h-4 w-4" />
                                                    <span>Email Script</span>
                                                </span>
                                                {expandedScript === point.id ? (
                                                    <ChevronUp className="h-4 w-4 text-slate-500" />
                                                ) : (
                                                    <ChevronDown className="h-4 w-4 text-slate-500" />
                                                )}
                                            </button>

                                            {expandedScript === point.id && (
                                                <div className="border-t border-white/5 p-4">
                                                    <pre className="text-xs text-slate-400 whitespace-pre-wrap font-sans leading-relaxed mb-4">
                                                        {point.script}
                                                    </pre>
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => copyScript(point.id, point.script)}
                                                        className="w-full"
                                                    >
                                                        <Copy className="h-3 w-3 mr-2" />
                                                        {copiedId === point.id ? 'Copied!' : 'Copy Script'}
                                                    </Button>
                                                </div>
                                            )}
                                        </div>

                                        {point.fallback && (
                                            <p className="mt-3 text-xs text-slate-500">
                                                <span className="font-bold text-gold">Fallback:</span> {point.fallback}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </CardContent>
                </Card>
            )}

            {/* AI Narration */}
            {narration && (
                <Card className="border-gold/10 bg-white/5 backdrop-blur-xl overflow-hidden">
                    <CardHeader className="bg-gold/5 border-b border-gold/10">
                        <CardTitle className="flex items-center space-x-2 text-gold">
                            <Sparkles className="h-5 w-5" />
                            <span>AI Insights</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6">
                        <div className="relative">
                            <MessageSquareQuote className="absolute -top-2 -left-2 h-8 w-8 text-gold/10" />
                            <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap pl-4">
                                {narration.summary}
                            </p>
                        </div>
                        <div className="mt-4 flex items-center space-x-4 text-xs text-slate-500 font-bold uppercase tracking-widest">
                            <span>Model: {narration.model}</span>
                            <span className="text-white/10">|</span>
                            <span>Confidence: {Math.round(narration.confidence * 100)}%</span>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Empty State */}
            {redFlags.length === 0 && favorableTerms.length === 0 && !narration && (
                <Card className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden">
                    <CardContent className="p-12 text-center">
                        <CheckCircle2 className="h-12 w-12 text-emerald-400 mx-auto mb-4" />
                        <h3 className="text-lg font-bold text-white mb-2">Looking Good!</h3>
                        <p className="text-sm text-slate-500">
                            No major red flags detected in your contract terms.
                        </p>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};
