import React, { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AnalyzeResponse, Severity } from '../lib/types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import {
    ArrowLeft,
    Download,
    Copy,
    Shield,
    TrendingUp,
    CheckCircle2,
    ChevronRight,
    Sparkles,
    Target,
    Zap,
    Scale,
    AlertCircle,
    Info,
    Calendar
} from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';
import { BellCurve } from '../components/analyze/BellCurve';
import { ClauseHeatmap } from '../components/analyze/ClauseHeatmap';
import { ScoreBreakdown } from '../components/analyze/ScoreBreakdown';

export const ResultsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const result = location.state?.result as AnalyzeResponse;

    if (!result) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-center space-y-6 bg-charcoal">
                <div className="h-20 w-20 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
                    <Shield className="h-10 w-10 text-slate-500" />
                </div>
                <div>
                    <h2 className="text-2xl font-serif text-white">Analysis Missing</h2>
                    <p className="text-slate-500 mt-2">No data retrieved from the engine.</p>
                </div>
                <Button variant="primary" onClick={() => navigate('/')} className="btn-primary">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Ingestion
                </Button>
            </div>
        );
    }

    const { extraction, scoring, red_flags, favorable_terms, negotiation_points, percentiles, narration, timings } = result;

    const handleCopy = () => {
        const text = [
            `FairDeal Analysis: ${result.contract_metadata?.role_title || 'Contract'}`,
            `Score: ${Math.round(scoring.overall_score)}/100 (${scoring.grade})`,
            `Salary: ${extraction.ctc_inr?.value ? '₹' + (extraction.ctc_inr.value / 100000).toFixed(1) + 'L' : 'N/A'}`,
            `Notice: ${extraction.notice_period_days?.value || 'N/A'} days`,
            `Risks: ${red_flags.length} detected`,
        ].join('\\n');
        navigator.clipboard.writeText(text);
        alert("Analysis summary copied to clipboard");
    };

    const handleDownload = () => {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `fairdeal_analysis_${Date.now()}.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    return (
        <div className="relative min-h-screen pt-24 pb-20 px-4 overflow-hidden bg-[#050505]">
            <div className="fixed inset-0 animated-grid pointer-events-none opacity-10" />

            <div className="relative z-10 max-w-7xl mx-auto space-y-10">
                {/* Top Nav / Actions */}
                <div className="flex items-center justify-between">
                    <button
                        onClick={() => navigate('/')}
                        className="group flex items-center gap-2 text-xs font-black uppercase tracking-[0.2em] text-slate-500 hover:text-gold transition-colors"
                    >
                        <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                        Re-Ingest Contract
                    </button>
                    <div className="flex gap-4">
                        <button onClick={handleCopy} className="p-3 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:text-gold transition-colors" title="Copy Summary">
                            <Copy className="h-4 w-4" />
                        </button>
                        <button onClick={handleDownload} className="p-3 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:text-gold transition-colors" title="Download JSON">
                            <Download className="h-4 w-4" />
                        </button>
                    </div>
                </div>

                {/* HERO: SCORE & SUMMARY */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Left: Overall Score Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="lg:col-span-4"
                    >
                        <Card className="liquid-glass p-10 h-full flex flex-col items-center justify-center text-center relative overflow-hidden group">
                            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-gold to-transparent opacity-50" />

                            <span className="text-xs font-black uppercase tracking-[0.3em] text-slate-500 mb-8">Contract Fairness Score</span>

                            <div className="relative mb-8">
                                <svg className="h-48 w-48" viewBox="0 0 100 100">
                                    <circle className="text-white/5" strokeWidth="4" stroke="currentColor" fill="transparent" r="45" cx="50" cy="50" />
                                    <motion.circle
                                        initial={{ strokeDashoffset: 2 * Math.PI * 45 }}
                                        animate={{ strokeDashoffset: 2 * Math.PI * 45 * (1 - scoring.overall_score / 100) }}
                                        transition={{ duration: 2, ease: "easeOut" }}
                                        strokeWidth="4"
                                        strokeDasharray={2 * Math.PI * 45}
                                        strokeLinecap="round"
                                        stroke="#D4AF37"
                                        fill="transparent"
                                        r="45"
                                        cx="50"
                                        cy="50"
                                        transform="rotate(-90 50 50)"
                                        className="drop-shadow-[0_0_8px_rgba(212,175,55,0.5)]"
                                    />
                                </svg>
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className="text-7xl font-serif font-bold text-white leading-none">
                                        {Math.round(scoring.overall_score)}
                                    </span>
                                    <span className="text-sm font-black uppercase tracking-widest text-gold mt-2">{scoring.grade}</span>
                                    {scoring.badges && scoring.badges.length > 0 && (
                                        <div className="flex flex-col gap-1 mt-3 items-center">
                                            {scoring.badges.map(badge => (
                                                <span key={badge} className="px-2 py-0.5 rounded-full bg-gold/20 text-[10px] font-bold text-gold border border-gold/30">
                                                    {badge}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 w-full">
                                <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wider mb-2">Mathematical Breakdown</p>
                                <p className="text-[11px] font-mono text-gold/80 break-all">{scoring.score_formula}</p>
                            </div>
                        </Card>

                        <div className="mt-8">
                            <ScoreBreakdown scoring={scoring} />
                        </div>
                    </motion.div>

                    {/* Right: AI Narration & Context */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="lg:col-span-8 flex flex-col space-y-8"
                    >
                        <Card className="liquid-glass p-10 flex-1 relative overflow-hidden">
                            <div className="absolute top-6 right-8">
                                <Sparkles className="h-6 w-6 text-gold/20" />
                            </div>
                            <h2 className="text-3xl font-serif text-white mb-6 italic">The Verdict</h2>
                            <p className="text-xl text-slate-300 leading-relaxed font-sans first-letter:text-5xl first-letter:font-serif first-letter:text-gold first-letter:mr-3 first-letter:float-left">
                                {narration?.summary || "No executive summary available for this analysis."}
                            </p>

                            <div className="mt-10 flex flex-wrap gap-4">
                                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10">
                                    <Target className="h-4 w-4 text-gold" />
                                    <span className="text-xs font-bold text-slate-300 uppercase tracking-widest">{result.contract_metadata.role_title}</span>
                                </div>
                                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10">
                                    <Scale className="h-4 w-4 text-amber" />
                                    <span className="text-xs font-bold text-slate-300 uppercase tracking-widest">Confidence: {Math.round(scoring.score_confidence * 100)}%</span>
                                </div>
                                <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 ml-auto">
                                    <Zap className="h-4 w-4 text-blue-400" />
                                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Calculated in {(timings.total_ms / 1000).toFixed(2)}s</span>
                                </div>
                            </div>
                        </Card>

                        {/* Quick Metrics Bar */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <MetricBox icon={TrendingUp} label="Annual CTC" value={extraction.ctc_inr?.value ? `₹${(extraction.ctc_inr.value / 100000).toFixed(1)}L` : 'N/A'} color="text-gold" />
                            <MetricBox icon={Calendar} label="Notice Period" value={extraction.notice_period_days?.value ? `${extraction.notice_period_days.value} Days` : 'N/A'} color="text-blue-400" />
                            <MetricBox icon={Shield} label="Bond Amount" value={extraction.bond_amount_inr?.value ? `₹${(extraction.bond_amount_inr.value / 100000).toFixed(1)}L` : 'NONE'} color="text-red-400" />
                            <MetricBox icon={Target} label="Benefits" value={`${extraction.benefits_count || 0} Count`} color="text-emerald-400" />
                        </div>
                    </motion.div>
                </div>

                {/* MID: VISUALIZATIONS */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    {/* Salary Percentile / Bell Curve */}
                    <Card className="lg:col-span-7 liquid-glass p-8 border-gold/10">
                        <div className="flex items-center justify-between mb-4">
                            <div className="space-y-1">
                                <h3 className="text-lg font-bold text-white uppercase tracking-widest flex items-center gap-2">
                                    Market Positioning
                                </h3>
                                <p className="text-xs text-slate-500">Benchmark vs. {percentiles.salary?.cohort_size || 0} Professional Contracts</p>
                            </div>
                            <div className="text-right">
                                <span className="text-4xl font-serif text-gold font-bold">
                                    {percentiles.salary ? Math.round(percentiles.salary.value) + 'th' : 'N/A'}
                                </span>
                                <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Percentile</p>
                            </div>
                        </div>
                        <BellCurve percentile={percentiles.salary?.value || 50} label="Salary Positioning" />
                        <div className="mt-8 grid grid-cols-3 gap-4 border-t border-white/5 pt-6">
                            <div className="text-center">
                                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Market Median</p>
                                <p className="text-sm font-bold text-white">
                                    {result.benchmark?.market_median ? `₹${(result.benchmark.market_median / 100000).toFixed(1)}L` : 'N/A'}
                                </p>
                            </div>
                            <div className="text-center border-x border-white/5">
                                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Top 25%</p>
                                <p className="text-sm font-bold text-white">
                                    {result.benchmark?.market_p75 ? `₹${(result.benchmark.market_p75 / 100000).toFixed(1)}L+` : 'N/A'}
                                </p>
                            </div>
                            <div className="text-center">
                                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Market Mean</p>
                                <p className="text-sm font-bold text-white">
                                    {result.benchmark?.market_mean ? `₹${(result.benchmark.market_mean / 100000).toFixed(1)}L` : 'N/A'}
                                </p>
                            </div>
                        </div>
                    </Card>

                    {/* Risk Heatmap */}
                    <Card className="lg:col-span-5 liquid-glass p-8 border-white/5 flex flex-col justify-between">
                        <ClauseHeatmap
                            score={scoring.safety_score}
                            label="Risk profile"
                            clauses={[
                                {
                                    type: 'Termination',
                                    risk: extraction.notice_period_days?.value
                                        ? (extraction.notice_period_days.value > 60 ? 'high' : extraction.notice_period_days.value > 30 ? 'medium' : 'low')
                                        : 'low',
                                    score: extraction.notice_period_days?.value
                                        ? Math.max(0, 100 - (extraction.notice_period_days.value - 30) * 2)
                                        : 90
                                },
                                {
                                    type: 'Non Compete',
                                    risk: extraction.non_compete_months?.value
                                        ? (extraction.non_compete_months.value > 12 ? 'high' : extraction.non_compete_months.value > 6 ? 'medium' : 'low')
                                        : 'low',
                                    score: extraction.non_compete_months?.value
                                        ? Math.max(0, 100 - extraction.non_compete_months.value * 5)
                                        : 100
                                },
                                {
                                    type: 'Bond',
                                    risk: extraction.bond_amount_inr?.value
                                        ? (extraction.bond_amount_inr.value > 100000 ? 'high' : extraction.bond_amount_inr.value > 50000 ? 'medium' : 'low')
                                        : 'low',
                                    score: extraction.bond_amount_inr?.value
                                        ? Math.max(0, 100 - (extraction.bond_amount_inr.value / 10000))
                                        : 100
                                },
                                {
                                    type: 'Probation',
                                    risk: extraction.probation_months?.value
                                        ? (extraction.probation_months.value > 6 ? 'high' : extraction.probation_months.value > 3 ? 'medium' : 'low')
                                        : 'low',
                                    score: extraction.probation_months?.value
                                        ? Math.max(0, 100 - (extraction.probation_months.value - 3) * 10)
                                        : 90
                                },
                            ]}
                        />
                        <div className="mt-6 p-4 rounded-xl bg-white/5 flex items-start gap-3">
                            <Info className="h-4 w-4 text-slate-400 shrink-0 mt-1" />
                            <p className="text-[11px] text-slate-500">
                                This heatmap is generated by comparing your contract clauses against legal standards and precedent data. Red fields indicate potential high-risk or restrictive language.
                            </p>
                        </div>
                    </Card>
                </div>

                {/* BOTTOM: RISK / FAV / NEGOTIATION */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Red Flags - Gourmet Version */}
                    <div className="space-y-6">
                        <div className="flex items-center gap-4">
                            <h3 className="text-xl font-serif text-white italic">Critical Risks</h3>
                            <div className="h-[1px] flex-1 bg-gradient-to-r from-red-500/20 to-transparent" />
                        </div>
                        <div className="space-y-4">
                            {red_flags.map((flag, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, x: -20 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: true }}
                                    className="p-6 rounded-2xl bg-white/5 border-l-4 border-red-500/50 border-white/5 relative group hover:bg-white/10 transition-all"
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-red-400">{flag.severity}</span>
                                        <span className="text-xs font-mono text-slate-600">-{flag.impact_score} PTS</span>
                                    </div>
                                    <h4 className="text-lg font-bold text-white mb-2">{flag.rule}</h4>
                                    <p className="text-sm text-slate-400 mb-4">{flag.explanation}</p>
                                    <div className="flex items-center gap-3 text-[11px] font-bold text-gold uppercase tracking-wider">
                                        <ChevronRight className="h-3 w-3" />
                                        Strategy: {flag.recommendation}
                                    </div>
                                    {flag.source_text && (
                                        <div className="mt-4 p-3 rounded-lg bg-black text-[10px] font-mono text-slate-500 italic opacity-0 group-hover:opacity-100 transition-opacity">
                                            "{flag.source_text.substring(0, 150)}..."
                                        </div>
                                    )}
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    {/* Negotiation - Gourmet Version */}
                    <div className="space-y-6">
                        <div className="flex items-center gap-4">
                            <h3 className="text-xl font-serif text-white italic">Negotiation Playbook</h3>
                            <div className="h-[1px] flex-1 bg-gradient-to-r from-gold/20 to-transparent" />
                        </div>
                        <div className="space-y-4">
                            {negotiation_points.map((point, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, x: 20 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: true }}
                                    className="p-6 rounded-2xl liquid-glass border-gold/10"
                                >
                                    <div className="flex items-center justify-between mb-4">
                                        <h4 className="text-lg font-bold text-white">{point.topic}</h4>
                                        <span className={cn(
                                            "px-2 py-1 rounded text-[10px] font-black uppercase tracking-widest",
                                            point.success_probability === 'High' ? "bg-emerald-500/20 text-emerald-400" :
                                                point.success_probability === 'Medium' ? "bg-amber-500/20 text-amber-400" :
                                                    "bg-red-500/20 text-red-400"
                                        )}>
                                            {point.success_probability} Chance
                                        </span>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div className="p-3 rounded-xl bg-white/5">
                                            <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Current</p>
                                            <p className="text-sm text-slate-300">{point.current_term}</p>
                                        </div>
                                        <div className="p-3 rounded-xl bg-gold/5 border border-gold/10">
                                            <p className="text-[10px] text-gold uppercase font-bold tracking-widest mb-1">Target</p>
                                            <p className="text-sm text-gold font-bold">{point.target_term}</p>
                                        </div>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-6 italic">"{point.rationale}"</p>

                                    <details className="group">
                                        <summary className="cursor-pointer list-none flex items-center gap-2 text-xs font-bold text-gold uppercase tracking-widest hover:text-white transition-colors">
                                            <div className="h-4 w-4 rounded-full bg-gold/20 flex items-center justify-center group-open:rotate-180 transition-transform">
                                                <ChevronRight className="h-3 w-3" />
                                            </div>
                                            Reveal Negotiation Script
                                        </summary>
                                        <div className="mt-4 p-5 rounded-2xl bg-black/50 border border-white/5 font-mono text-sm leading-relaxed text-slate-400 relative">
                                            <Copy className="absolute top-4 right-4 h-4 w-4 text-slate-700 hover:text-gold cursor-pointer" />
                                            {point.script}
                                        </div>
                                    </details>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const MetricBox = ({ icon: Icon, label, value, color }: { icon: any, label: string, value: string, color: string }) => (
    <div className="p-5 rounded-3xl liquid-glass border-white/5 flex flex-col gap-2">
        <div className={cn("p-2 rounded-xl bg-white/5 w-fit", color)}>
            <Icon className="h-4 w-4" />
        </div>
        <div>
            <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest leading-none mb-1">{label}</p>
            <p className="text-lg font-serif font-bold text-white leading-tight">{value}</p>
        </div>
    </div>
);
