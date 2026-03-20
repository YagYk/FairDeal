import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { AnalyzeResponse, EvidenceChunk, ContractExtractionResult, ScoreResult, RedFlag } from '../lib/types';
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
    AlertTriangle,
    Info,
    Calendar,
    Database,
    BookOpen,
    FileText,
    Clock,
    Award,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';
import { BellCurve } from '../components/analyze/BellCurve';
import { ClauseHeatmap } from '../components/analyze/ClauseHeatmap';
import { ScoreBreakdown } from '../components/analyze/ScoreBreakdown';

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

const getOrdinalSuffix = (num: number): string => {
    const j = num % 10;
    const k = num % 100;
    if (j === 1 && k !== 11) return num + 'st';
    if (j === 2 && k !== 12) return num + 'nd';
    if (j === 3 && k !== 13) return num + 'rd';
    return num + 'th';
};

/** Format INR amount smartly — shows lakhs for large amounts, thousands for smaller ones */
const formatLakhs = (val: number | null | undefined): string => {
    if (val === null || val === undefined || val === 0) return 'N/A';
    if (val >= 100000) {
        // Show in lakhs with 2 decimal precision, drop trailing zeros
        const lakhs = val / 100000;
        const formatted = lakhs.toFixed(2).replace(/\.?0+$/, '');
        return `₹${formatted}L`;
    }
    if (val >= 1000) {
        // Show in thousands
        const thousands = val / 1000;
        const formatted = thousands.toFixed(1).replace(/\.?0+$/, '');
        return `₹${formatted}K`;
    }
    // Small amount: show as-is
    return `₹${val.toLocaleString('en-IN')}`;
};

/** Safely truncate long text with ellipsis */
const truncate = (text: string | null | undefined, max = 120): string => {
    if (!text) return '';
    const clean = text.replace(/\n/g, ' ').trim();
    return clean.length > max ? clean.slice(0, max) + '...' : clean;
};

/** Format ms timing nicely */
const formatTime = (ms: number): string => {
    if (ms < 1000) return `${Math.round(ms)}ms`;
    const s = ms / 1000;
    if (s < 60) return `${s.toFixed(1)}s`;
    return `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
};

/** Build real heatmap clauses from extraction + scoring + red flags */
const buildHeatmapClauses = (
    extraction: ContractExtractionResult,
    scoring: ScoreResult,
    red_flags: RedFlag[],
    noticeVal: number | null,
    bondVal: number | null,
) => {
    type ClauseData = {
        label: string;
        status: 'safe' | 'caution' | 'risk' | 'danger' | 'unknown';
        detail: string;
        impact: number;
    };

    const statusFromScore = (s: number): ClauseData['status'] =>
        s >= 80 ? 'safe' : s >= 60 ? 'caution' : s >= 40 ? 'risk' : 'danger';

    // Count red flags by keyword matching for each category
    const flagsFor = (keywords: string[]) =>
        red_flags.filter(f =>
            keywords.some(k =>
                f.rule.toLowerCase().includes(k) ||
                f.explanation.toLowerCase().includes(k)
            )
        );

    // Penalty from red flags: each critical=-20, high=-15, medium=-10, low=-5
    const flagPenalty = (flags: RedFlag[]): number =>
        flags.reduce((sum, f) => {
            if (f.severity === 'critical') return sum + 20;
            if (f.severity === 'high') return sum + 15;
            if (f.severity === 'medium') return sum + 10;
            return sum + 5;
        }, 0);

    const clauses: ClauseData[] = [];

    // ── 1. Termination / Notice Period ──
    const termFlags = flagsFor(['notice', 'terminat', 'resignation', 'at-will', 'at will']);
    if (noticeVal !== null) {
        let score = 85; // baseline for having a notice period
        if (noticeVal > 90) score = 25;       // >3 months: very restrictive
        else if (noticeVal > 60) score = 45;   // >2 months: restrictive
        else if (noticeVal > 30) score = 65;   // >1 month: moderate
        else if (noticeVal >= 15) score = 85;  // 15-30 days: standard
        else score = 75;                        // very short: slightly unusual

        score = Math.max(0, score - flagPenalty(termFlags));
        clauses.push({
            label: 'Termination / Notice',
            status: statusFromScore(score),
            detail: `${Math.round(noticeVal)} day notice period${termFlags.length ? ` · ${termFlags.length} risk${termFlags.length > 1 ? 's' : ''}` : ''}`,
            impact: score,
        });
    } else {
        // Notice period not found — that's risky, not safe
        const penalty = flagPenalty(termFlags);
        const score = Math.max(0, 50 - penalty); // unknown = 50 baseline, minus flags
        clauses.push({
            label: 'Termination / Notice',
            status: termFlags.length > 0 ? statusFromScore(score) : 'unknown',
            detail: termFlags.length > 0
                ? `Not extracted · ${termFlags.length} risk${termFlags.length > 1 ? 's' : ''} flagged`
                : 'Notice period not found in contract',
            impact: score,
        });
    }

    // ── 2. Non-Compete ──
    const ncFlags = flagsFor(['non-compete', 'non compete', 'noncompete', 'restrictive covenant', 'restraint']);
    const ncMonths = extraction.non_compete_months?.value;
    if (ncMonths !== null && ncMonths !== undefined && ncMonths > 0) {
        let score = 80;
        if (ncMonths > 24) score = 15;          // >2 years: extreme
        else if (ncMonths > 12) score = 30;     // >1 year: very restrictive
        else if (ncMonths > 6) score = 50;      // 7-12 months: restrictive
        else if (ncMonths > 3) score = 65;      // 4-6 months: moderate
        else score = 80;                         // ≤3 months: mild

        score = Math.max(0, score - flagPenalty(ncFlags));
        clauses.push({
            label: 'Non-Compete',
            status: statusFromScore(score),
            detail: `${ncMonths} month restriction${ncFlags.length ? ` · ${ncFlags.length} risk${ncFlags.length > 1 ? 's' : ''}` : ''}`,
            impact: score,
        });
    } else if (ncFlags.length > 0) {
        // No months extracted but red flags exist
        const score = Math.max(0, 60 - flagPenalty(ncFlags));
        clauses.push({
            label: 'Non-Compete',
            status: statusFromScore(score),
            detail: `${ncFlags.length} risk${ncFlags.length > 1 ? 's' : ''} flagged`,
            impact: score,
        });
    } else {
        // No non-compete found — this is actually favorable
        clauses.push({
            label: 'Non-Compete',
            status: 'safe',
            detail: 'No non-compete clause detected',
            impact: 90,
        });
    }

    // ── 3. Bond / Service Agreement ──
    const bondFlags = flagsFor(['bond', 'service agreement', 'training bond', 'liquidated damage', 'penalty', 'lock-in', 'lockin']);
    if (bondVal !== null && bondVal > 0) {
        let score = 70;
        if (bondVal > 500000) score = 15;         // >5L: extreme
        else if (bondVal > 200000) score = 30;    // 2-5L: heavy
        else if (bondVal > 100000) score = 45;    // 1-2L: significant
        else if (bondVal > 50000) score = 60;     // 50K-1L: moderate
        else score = 75;                           // <50K: light

        score = Math.max(0, score - flagPenalty(bondFlags));
        const amtStr = bondVal >= 100000
            ? `₹${(bondVal / 100000).toFixed(1).replace(/\.0$/, '')}L`
            : `₹${(bondVal / 1000).toFixed(0)}K`;
        clauses.push({
            label: 'Bond / Service Agreement',
            status: statusFromScore(score),
            detail: `${amtStr} bond amount${bondFlags.length ? ` · ${bondFlags.length} risk${bondFlags.length > 1 ? 's' : ''}` : ''}`,
            impact: score,
        });
    } else if (bondFlags.length > 0) {
        const score = Math.max(0, 60 - flagPenalty(bondFlags));
        clauses.push({
            label: 'Bond / Service Agreement',
            status: statusFromScore(score),
            detail: `${bondFlags.length} risk${bondFlags.length > 1 ? 's' : ''} flagged`,
            impact: score,
        });
    } else {
        clauses.push({
            label: 'Bond / Service Agreement',
            status: 'safe',
            detail: 'No bond or service agreement detected',
            impact: 95,
        });
    }

    // ── 4. Probation ──
    const probFlags = flagsFor(['probation', 'confirmation', 'trial period']);
    const probMonths = extraction.probation_months?.value;
    if (probMonths !== null && probMonths !== undefined && probMonths > 0) {
        let score = 80;
        if (probMonths > 12) score = 25;         // >1 year: very unusual
        else if (probMonths > 6) score = 45;     // >6 months: long
        else if (probMonths > 3) score = 65;     // 4-6 months: standard-ish
        else score = 85;                          // ≤3 months: short

        score = Math.max(0, score - flagPenalty(probFlags));
        clauses.push({
            label: 'Probation Period',
            status: statusFromScore(score),
            detail: `${probMonths} month${probMonths > 1 ? 's' : ''} probation${probFlags.length ? ` · ${probFlags.length} risk${probFlags.length > 1 ? 's' : ''}` : ''}`,
            impact: score,
        });
    } else {
        clauses.push({
            label: 'Probation Period',
            status: probFlags.length > 0 ? statusFromScore(Math.max(0, 60 - flagPenalty(probFlags))) : 'unknown',
            detail: probFlags.length > 0
                ? `${probFlags.length} risk${probFlags.length > 1 ? 's' : ''} flagged`
                : 'Probation period not specified',
            impact: probFlags.length > 0 ? Math.max(0, 60 - flagPenalty(probFlags)) : 50,
        });
    }

    // ── 5. Legal Compliance (PF, Gratuity, etc.) ──
    const legalViolations = scoring.legal_violations || [];
    const legalFlags = flagsFor(['pf', 'provident fund', 'gratuity', 'esi', 'statutory', 'compliance', 'legal']);
    if (legalViolations.length > 0 || legalFlags.length > 0) {
        const score = Math.max(0, 80 - legalViolations.length * 20 - flagPenalty(legalFlags));
        clauses.push({
            label: 'Legal Compliance',
            status: statusFromScore(score),
            detail: legalViolations.length > 0
                ? `${legalViolations.length} violation${legalViolations.length > 1 ? 's' : ''}: ${legalViolations[0]?.substring(0, 50)}...`
                : `${legalFlags.length} compliance concern${legalFlags.length > 1 ? 's' : ''}`,
            impact: score,
        });
    } else {
        clauses.push({
            label: 'Legal Compliance',
            status: 'safe',
            detail: 'No statutory compliance issues detected',
            impact: 85,
        });
    }

    // ── 6. IP / Confidentiality ──
    const ipFlags = flagsFor(['ip', 'intellectual property', 'invention', 'confidential', 'nda', 'trade secret', 'proprietary']);
    if (ipFlags.length > 0) {
        const score = Math.max(0, 75 - flagPenalty(ipFlags));
        clauses.push({
            label: 'IP & Confidentiality',
            status: statusFromScore(score),
            detail: `${ipFlags.length} clause${ipFlags.length > 1 ? 's' : ''} flagged`,
            impact: score,
        });
    } else {
        // Not flagged = likely standard IP terms
        clauses.push({
            label: 'IP & Confidentiality',
            status: 'safe',
            detail: 'Standard or no IP restrictions',
            impact: 82,
        });
    }

    // ── 7. Remaining uncategorized red flags ──
    const categorizedKeywords = [
        'notice', 'terminat', 'resignation', 'at-will', 'at will',
        'non-compete', 'non compete', 'noncompete', 'restrictive covenant', 'restraint',
        'bond', 'service agreement', 'training bond', 'liquidated damage', 'penalty', 'lock-in', 'lockin',
        'probation', 'confirmation', 'trial period',
        'pf', 'provident fund', 'gratuity', 'esi', 'statutory', 'compliance', 'legal',
        'ip', 'intellectual property', 'invention', 'confidential', 'nda', 'trade secret', 'proprietary',
    ];
    const uncategorized = red_flags.filter(f =>
        !categorizedKeywords.some(k =>
            f.rule.toLowerCase().includes(k) || f.explanation.toLowerCase().includes(k)
        )
    );
    if (uncategorized.length > 0) {
        const score = Math.max(0, 70 - flagPenalty(uncategorized));
        clauses.push({
            label: 'Other Clauses',
            status: statusFromScore(score),
            detail: `${uncategorized.length} additional concern${uncategorized.length > 1 ? 's' : ''}: ${uncategorized[0]?.rule?.substring(0, 40)}`,
            impact: score,
        });
    }

    return clauses;
};

/** Check if the benchmark data is actually usable (not all zeros) */
const hasBenchmarkData = (b: AnalyzeResponse['benchmark']): boolean => {
    if (!b) return false;
    return (b.cohort_size > 0 && (b.market_mean > 0 || b.market_median > 0));
};

/** Check if percentile data exists */
const hasPercentileData = (p: AnalyzeResponse['percentiles']): boolean => {
    return p && Object.keys(p).length > 0 && !!p.salary;
};

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export const ResultsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const result = location.state?.result as AnalyzeResponse;

    if (!result) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
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

    // Derived flags
    const benchmarkUsable = hasBenchmarkData(result.benchmark);
    const percentileUsable = hasPercentileData(percentiles);
    const salaryVal = extraction.ctc_inr?.value ?? null;
    const noticeVal = extraction.notice_period_days?.value ?? null;
    const bondVal = extraction.bond_amount_inr?.value ?? null;

    const handleCopy = () => {
        const text = [
            `FairDeal Analysis: ${result.contract_metadata?.role_title || 'Contract'}`,
            `Score: ${Math.round(scoring.overall_score)}/100 (${scoring.grade})`,
            `Salary: ${salaryVal ? formatLakhs(salaryVal) : 'N/A'}`,
            `Notice: ${noticeVal ?? 'N/A'} days`,
            `Risks: ${red_flags.length} detected`,
        ].join('\n');
        navigator.clipboard.writeText(text);
    };

    const handleDownload = () => {
        const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(result, null, 2));
        const a = document.createElement('a');
        a.setAttribute('href', dataStr);
        a.setAttribute('download', `fairdeal_analysis_${Date.now()}.json`);
        document.body.appendChild(a);
        a.click();
        a.remove();
    };

    return (
        <div className="relative pb-10 overflow-hidden">
            <div className="absolute inset-0 animated-grid pointer-events-none opacity-10" />

            <div className="relative z-10 space-y-8">
                {/* ── Top Nav / Actions ── */}
                <div className="flex items-center justify-between">
                    <button
                        onClick={() => navigate('/')}
                        className="group flex items-center gap-2 text-xs font-black uppercase tracking-[0.2em] text-slate-500 hover:text-gold transition-colors"
                    >
                        <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                        Re-Ingest Contract
                    </button>
                    <div className="flex gap-3">
                        <button onClick={handleCopy} className="p-2.5 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:text-gold transition-colors" title="Copy Summary">
                            <Copy className="h-4 w-4" />
                        </button>
                        <button onClick={handleDownload} className="p-2.5 rounded-full bg-white/5 border border-white/10 text-slate-400 hover:text-gold transition-colors" title="Download JSON">
                            <Download className="h-4 w-4" />
                        </button>
                    </div>
                </div>

                {/* ═══════════════════════════════════════════════════ */}
                {/*  HERO: SCORE + SUMMARY                            */}
                {/* ═══════════════════════════════════════════════════ */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left: Score Ring */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="lg:col-span-4">
                        <Card className="liquid-glass p-6 flex flex-col items-center text-center relative overflow-hidden">
                            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-transparent via-gold to-transparent opacity-50" />

                            <span className="text-[9px] font-black uppercase tracking-[0.25em] text-slate-500 mb-4">Contract Fairness Score</span>

                            <div className="relative mb-4">
                                <svg className="h-36 w-36" viewBox="0 0 100 100">
                                    <circle className="text-white/5" strokeWidth="4" stroke="currentColor" fill="transparent" r="45" cx="50" cy="50" />
                                    <motion.circle
                                        initial={{ strokeDashoffset: 2 * Math.PI * 45 }}
                                        animate={{ strokeDashoffset: 2 * Math.PI * 45 * (1 - scoring.overall_score / 100) }}
                                        transition={{ duration: 2, ease: 'easeOut' }}
                                        strokeWidth="4"
                                        strokeDasharray={2 * Math.PI * 45}
                                        strokeLinecap="round"
                                        stroke="#D4AF37"
                                        fill="transparent"
                                        r="45" cx="50" cy="50"
                                        transform="rotate(-90 50 50)"
                                        className="drop-shadow-[0_0_8px_rgba(212,175,55,0.5)]"
                                    />
                                </svg>
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <span className="text-5xl font-serif font-bold text-white leading-none">
                                        {Math.round(scoring.overall_score)}
                                    </span>
                                    <span className="text-[10px] font-black uppercase tracking-widest text-gold mt-1">{scoring.grade}</span>
                                    {scoring.badges && scoring.badges.length > 0 && (
                                        <div className="flex flex-wrap gap-1 mt-2 justify-center">
                                            {scoring.badges.map(badge => (
                                                <span key={badge} className="px-2 py-0.5 rounded-full bg-gold/20 text-[9px] font-bold text-gold border border-gold/30">
                                                    {badge}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Quick summary chips */}
                            <div className="grid grid-cols-2 gap-2 w-full">
                                <MiniStat label="Safety" value={`${Math.round(scoring.safety_score)}/100`} />
                                <MiniStat label="Market" value={`${Math.round(scoring.market_fairness_score)}/100`} />
                            </div>
                        </Card>

                        <div className="mt-4">
                            <ScoreBreakdown scoring={scoring} />
                        </div>
                    </motion.div>

                    {/* Right: Verdict + Metrics */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="lg:col-span-8 flex flex-col gap-6">
                        {/* The Verdict */}
                        <Card className="liquid-glass p-6 flex-1 relative overflow-hidden">
                            <div className="absolute top-4 right-5">
                                <Sparkles className="h-4 w-4 text-gold/20" />
                            </div>
                            <h2 className="text-lg font-serif text-white mb-3 italic">The Verdict</h2>

                            {narration?.summary ? (
                                <p className="text-sm text-slate-300 leading-relaxed font-sans first-letter:text-3xl first-letter:font-serif first-letter:text-gold first-letter:mr-2 first-letter:float-left">
                                    {narration.summary}
                                </p>
                            ) : (
                                <div className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-start gap-3">
                                    <Info className="h-4 w-4 text-slate-500 shrink-0 mt-0.5" />
                                    <div>
                                        <p className="text-sm text-slate-400">AI narration was not generated for this analysis (the LLM may have been rate-limited).</p>
                                        <p className="text-xs text-slate-600 mt-1">The scoring and extraction are fully deterministic and remain accurate.</p>
                                    </div>
                                </div>
                            )}

                            <div className="mt-6 flex flex-wrap gap-3">
                                <Chip icon={Target} label={result.contract_metadata?.role_title || 'Contract'} />
                                <Chip icon={Scale} label={`Confidence: ${Math.round(scoring.score_confidence * 100)}%`} />
                                {result.contract_metadata?.company_name && result.contract_metadata.company_name.length < 60 && (
                                    <Chip icon={Award} label={result.contract_metadata.company_name} />
                                )}
                                <div className="ml-auto">
                                    <Chip icon={Clock} label={`Processed in ${formatTime(timings.total_ms)}`} muted />
                                </div>
                            </div>
                        </Card>

                        {/* Quick Metrics */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <MetricBox icon={TrendingUp} label="Annual CTC" value={salaryVal ? formatLakhs(salaryVal) : 'N/A'} color="text-gold" />
                            <MetricBox icon={Calendar} label="Notice Period" value={noticeVal ? `${Math.round(noticeVal)} Days` : 'Not Found'} color="text-blue-400" />
                            <MetricBox icon={Shield} label="Bond Amount" value={bondVal ? formatLakhs(bondVal) : 'None'} color="text-red-400" />
                            <MetricBox icon={Target} label="Benefits" value={`${extraction.benefits_count || 0} Found`} color="text-emerald-400" />
                        </div>
                    </motion.div>
                </div>

                {/* ═══════════════════════════════════════════════════ */}
                {/*  MARKET POSITIONING + RISK HEATMAP                */}
                {/* ═══════════════════════════════════════════════════ */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Salary / Bell Curve */}
                    <Card className="lg:col-span-7 liquid-glass p-6 border-gold/10">
                        <div className="flex items-center justify-between mb-4">
                            <div className="space-y-1">
                                <h3 className="text-sm font-bold text-white uppercase tracking-widest flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4 text-gold" />
                                    Market Positioning
                                </h3>
                                {benchmarkUsable ? (
                                    <p className="text-xs text-slate-500">
                                        Benchmarked against {result.benchmark!.cohort_size} contracts
                                        {result.benchmark!.broaden_steps && result.benchmark!.broaden_steps.length > 0
                                            ? ' (broader comparison)'
                                            : ''}
                                    </p>
                                ) : (
                                    <p className="text-xs text-amber-500/70">Limited market data available for this role</p>
                                )}
                            </div>
                            {percentileUsable && (
                                <div className="text-right">
                                    <span className="text-2xl font-serif text-gold font-bold">
                                        {Math.round(percentiles.salary!.value) <= 0
                                            ? '<1st'
                                            : Math.round(percentiles.salary!.value) >= 100
                                                ? '>99th'
                                                : getOrdinalSuffix(Math.round(percentiles.salary!.value))}
                                    </span>
                                    <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Percentile</p>
                                </div>
                            )}
                        </div>

                        {percentileUsable ? (
                            <BellCurve percentile={percentiles.salary!.value} label="Salary Positioning" />
                        ) : (
                            <div className="flex flex-col items-center justify-center py-10 text-center">
                                <AlertTriangle className="h-8 w-8 text-amber-500/40 mb-3" />
                                <p className="text-sm text-slate-400 font-medium">Insufficient Market Data</p>
                                <p className="text-xs text-slate-600 mt-1 max-w-md">
                                    {result.benchmark?.warning || 'Not enough comparable contracts to generate a reliable salary percentile.'}
                                </p>
                                {result.benchmark?.broaden_steps && result.benchmark.broaden_steps.length > 0 && (
                                    <div className="mt-3 flex flex-wrap gap-2 justify-center">
                                        {result.benchmark.broaden_steps.map((step, i) => (
                                            <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-white/5 text-slate-500 border border-white/10">
                                                {step.replace(/_/g, ' ')}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {benchmarkUsable && (
                            <div className="mt-6 grid grid-cols-3 gap-3 border-t border-white/5 pt-4">
                                <MarketStat label="Market Median" value={formatLakhs(result.benchmark!.market_median)} />
                                <MarketStat label="Top 25%" value={formatLakhs(result.benchmark!.market_p75)} border />
                                <MarketStat label="Market Mean" value={formatLakhs(result.benchmark!.market_mean)} />
                            </div>
                        )}
                    </Card>

                    {/* Risk Heatmap */}
                    <Card className="lg:col-span-5 liquid-glass p-6 border-white/5 flex flex-col justify-between">
                        <ClauseHeatmap
                            clauses={buildHeatmapClauses(extraction, scoring, red_flags, noticeVal, bondVal)}
                        />
                        <div className="mt-4 p-3 rounded-xl bg-white/5 flex items-start gap-3">
                            <Info className="h-4 w-4 text-slate-500 shrink-0 mt-0.5" />
                            <p className="text-[11px] text-slate-600">
                                Each clause is scored 0-100 based on extracted terms, market standards, and legal compliance. Lower = more risk.
                            </p>
                        </div>
                    </Card>
                </div>

                {/* ═══════════════════════════════════════════════════ */}
                {/*  RED FLAGS + NEGOTIATION                          */}
                {/* ═══════════════════════════════════════════════════ */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Red Flags */}
                    <div className="space-y-4">
                        <SectionHeader
                            icon={AlertCircle}
                            title="Critical Risks"
                            count={red_flags.length}
                            countColor="text-red-400"
                            gradientFrom="from-red-500/20"
                        />

                        {red_flags.length === 0 ? (
                            <EmptyState icon={CheckCircle2} color="text-emerald-400" message="No critical risks detected in this contract." />
                        ) : (
                            <div className="space-y-3">
                                {red_flags.map((flag, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: -20 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        viewport={{ once: true }}
                                        className="p-4 rounded-xl bg-white/5 border-l-4 border-red-500/50 hover:bg-white/[0.07] transition-all"
                                    >
                                        <div className="flex justify-between items-start mb-1">
                                            <span className="text-[9px] font-black uppercase tracking-[0.2em] text-red-400">
                                                {flag.severity}
                                            </span>
                                            <span className="text-[9px] font-mono text-slate-600">-{flag.impact_score} pts</span>
                                        </div>
                                        <h4 className="text-xs font-bold text-white mb-1">{flag.rule}</h4>
                                        <p className="text-[11px] text-slate-400 mb-2 leading-relaxed">{flag.explanation}</p>

                                        {flag.market_context && (
                                            <p className="text-[11px] text-slate-500 mb-3 italic">
                                                {flag.market_context}
                                            </p>
                                        )}

                                        <div className="flex items-center gap-2 text-[10px] font-bold text-gold uppercase tracking-wider">
                                            <ChevronRight className="h-3 w-3" />
                                            {flag.recommendation}
                                        </div>

                                        {flag.source_text && (
                                            <div className="mt-3 p-2.5 rounded-lg bg-black/40 text-[10px] font-mono text-slate-600 italic leading-relaxed">
                                                &ldquo;{truncate(flag.source_text, 180)}&rdquo;
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Negotiation Playbook */}
                    <div className="space-y-4">
                        <SectionHeader
                            icon={Target}
                            title="Negotiation Playbook"
                            count={negotiation_points.length}
                            countColor="text-gold"
                            gradientFrom="from-gold/20"
                        />

                        {negotiation_points.length === 0 ? (
                            <EmptyState icon={CheckCircle2} color="text-emerald-400" message="No negotiation points identified." />
                        ) : (
                            <div className="space-y-3">
                                {negotiation_points.map((point, idx) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: 20 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        viewport={{ once: true }}
                                        className="p-4 rounded-xl liquid-glass border-gold/10"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="text-xs font-bold text-white">{point.topic}</h4>
                                            <ProbabilityBadge prob={point.success_probability} />
                                        </div>

                                        <div className="grid grid-cols-2 gap-3 mb-3">
                                            <div className="p-2.5 rounded-xl bg-white/5">
                                                <p className="text-[9px] text-slate-500 uppercase font-bold tracking-widest mb-0.5">Current</p>
                                                <p className="text-xs text-slate-300">{point.current_term}</p>
                                            </div>
                                            <div className="p-2.5 rounded-xl bg-gold/5 border border-gold/10">
                                                <p className="text-[9px] text-gold uppercase font-bold tracking-widest mb-0.5">Target</p>
                                                <p className="text-xs text-gold font-bold">{point.target_term}</p>
                                            </div>
                                        </div>

                                        <p className="text-xs text-slate-500 mb-4 italic leading-relaxed">&ldquo;{point.rationale}&rdquo;</p>

                                        <details className="group">
                                            <summary className="cursor-pointer list-none flex items-center gap-2 text-[10px] font-bold text-gold uppercase tracking-widest hover:text-white transition-colors">
                                                <div className="h-3.5 w-3.5 rounded-full bg-gold/20 flex items-center justify-center group-open:rotate-90 transition-transform">
                                                    <ChevronRight className="h-2.5 w-2.5" />
                                                </div>
                                                View Negotiation Script
                                            </summary>
                                            <div className="mt-3 p-4 rounded-xl bg-black/50 border border-white/5 text-xs leading-relaxed text-slate-400 break-words whitespace-pre-wrap max-h-60 overflow-y-auto">
                                                {point.script}
                                            </div>
                                        </details>
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* ═══════════════════════════════════════════════════ */}
                {/*  FAVORABLE TERMS                                  */}
                {/* ═══════════════════════════════════════════════════ */}
                {favorable_terms.length > 0 && (
                    <div className="space-y-4">
                        <SectionHeader
                            icon={CheckCircle2}
                            title="Favorable Terms"
                            count={favorable_terms.length}
                            countColor="text-emerald-400"
                            gradientFrom="from-emerald-500/20"
                        />
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {favorable_terms.map((term, idx) => (
                                <motion.div
                                    key={idx}
                                    initial={{ opacity: 0, y: 10 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    className="p-4 rounded-2xl bg-white/5 border-l-4 border-emerald-500/40 hover:bg-white/[0.07] transition-all"
                                >
                                    <div className="flex items-start justify-between mb-1.5">
                                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider">{term.term}</h4>
                                        <span className="text-[10px] font-mono text-emerald-500/60">+{term.impact_score} pts</span>
                                    </div>
                                    <p className="text-xs text-slate-400 mb-1 leading-relaxed">{term.explanation}</p>
                                    {term.value && <p className="text-[11px] text-slate-500">{term.value}</p>}
                                    {term.market_context && (
                                        <p className="text-[10px] text-slate-600 mt-1 italic">{term.market_context}</p>
                                    )}
                                </motion.div>
                            ))}
                        </div>
                    </div>
                )}

                {/* ═══════════════════════════════════════════════════ */}
                {/*  RAG EVIDENCE                                     */}
                {/* ═══════════════════════════════════════════════════ */}
                {result.rag && Object.keys(result.rag.evidence_by_clause_type || {}).length > 0 && (
                    <div className="space-y-4">
                        <SectionHeader
                            icon={Database}
                            title="Evidence from Knowledge Base"
                            count={result.evidence?.length ?? 0}
                            countColor="text-blue-400"
                            gradientFrom="from-blue-500/20"
                        />

                        <div className="p-3 rounded-xl bg-blue-500/5 border border-blue-500/10 flex items-start gap-3">
                            <BookOpen className="h-4 w-4 text-blue-400 shrink-0 mt-0.5" />
                            <p className="text-[11px] text-slate-500">
                                Similar clause excerpts retrieved from our contract knowledge base via semantic search (RAG). These provide market context for how other employers word comparable terms.
                            </p>
                        </div>

                        {Object.entries(result.rag.evidence_by_clause_type).map(([clauseType, chunks]) => {
                            if (!chunks || chunks.length === 0) return null;
                            const typedChunks = chunks as EvidenceChunk[];
                            return (
                                <div key={clauseType} className="space-y-2">
                                    <div className="flex items-center gap-2">
                                        <FileText className="h-3.5 w-3.5 text-slate-600" />
                                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                                            {clauseType.replace(/_/g, ' ')}
                                        </span>
                                        <span className="text-[10px] text-slate-600">&middot; {typedChunks.length} matches</span>
                                    </div>
                                    <div className="grid grid-cols-1 gap-2">
                                        {typedChunks.slice(0, 3).map((chunk, idx) => (
                                            <div
                                                key={idx}
                                                className="p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-blue-500/20 transition-all"
                                            >
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-[10px] font-mono text-slate-600">
                                                        {chunk.metadata?.filename || chunk.contract_id}
                                                    </span>
                                                    <div className="flex items-center gap-2">
                                                        <div className="h-1.5 w-10 rounded-full bg-white/10 overflow-hidden">
                                                            <div
                                                                className="h-full rounded-full bg-blue-400"
                                                                style={{ width: `${Math.round((chunk.similarity || 0) * 100)}%` }}
                                                            />
                                                        </div>
                                                        <span className="text-[10px] font-mono text-blue-400">
                                                            {Math.round((chunk.similarity || 0) * 100)}%
                                                        </span>
                                                    </div>
                                                </div>
                                                <p className="text-[11px] text-slate-500 leading-relaxed break-words">
                                                    {truncate(chunk.text_preview, 250)}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* ═══════════════════════════════════════════════════ */}
                {/*  FOOTER                                           */}
                {/* ═══════════════════════════════════════════════════ */}
                <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
                    <FooterStat label="Extraction" value={result.determinism?.extraction || 'N/A'} />
                    <FooterStat label="Scoring" value={result.determinism?.scoring || 'N/A'} />
                    <FooterStat label="KB Evidence" value={`${result.evidence?.length || 0} chunks`} highlight />
                    <FooterStat label="Cache" value={result.cache?.hit ? 'HIT' : 'MISS'} />
                    <FooterStat label="Pipeline" value={formatTime(timings.total_ms)} />
                </div>
            </div>
        </div>
    );
};

/* ------------------------------------------------------------------ */
/*  Sub-components                                                     */
/* ------------------------------------------------------------------ */

const MiniStat = ({ label, value }: { label: string; value: string }) => (
    <div className="p-2.5 rounded-xl bg-white/5 border border-white/10 text-center">
        <p className="text-[9px] text-slate-600 uppercase font-bold tracking-widest mb-0.5">{label}</p>
        <p className="text-sm font-bold text-white">{value}</p>
    </div>
);

const MetricBox = ({ icon: Icon, label, value, color }: { icon: any; label: string; value: string; color: string }) => (
    <div className="p-3.5 rounded-xl liquid-glass border-white/5 flex items-center gap-3 min-w-0">
        <div className={cn('p-2 rounded-lg bg-white/5 shrink-0', color)}>
            <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0">
            <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest leading-none mb-1">{label}</p>
            <p className="text-sm font-serif font-bold text-white leading-tight truncate">{value}</p>
        </div>
    </div>
);

const Chip = ({ icon: Icon, label, muted }: { icon: any; label: string; muted?: boolean }) => (
    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
        <Icon className={cn('h-3.5 w-3.5', muted ? 'text-slate-600' : 'text-gold')} />
        <span className={cn('text-[10px] font-bold uppercase tracking-widest', muted ? 'text-slate-600' : 'text-slate-300')}>
            {label}
        </span>
    </div>
);

const SectionHeader = ({ icon: Icon, title, count, countColor, gradientFrom }: {
    icon: any; title: string; count: number; countColor: string; gradientFrom: string;
}) => (
    <div className="flex items-center gap-3">
        <Icon className={cn('h-4 w-4', countColor)} />
        <h3 className="text-base font-serif text-white italic">{title}</h3>
        <div className={cn('h-[1px] flex-1 bg-gradient-to-r to-transparent', gradientFrom)} />
        <span className={cn('px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest', countColor)}>
            {count}
        </span>
    </div>
);

const EmptyState = ({ icon: Icon, color, message }: { icon: any; color: string; message: string }) => (
    <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/5 flex items-center gap-3">
        <Icon className={cn('h-5 w-5', color)} />
        <p className="text-sm text-slate-500">{message}</p>
    </div>
);

const ProbabilityBadge = ({ prob }: { prob: string }) => {
    const isHigh = prob.toLowerCase().includes('high');
    const isMedium = prob.toLowerCase().includes('medium');
    return (
        <span className={cn(
            'px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest',
            isHigh ? 'bg-emerald-500/20 text-emerald-400' :
                isMedium ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'
        )}>
            {prob}
        </span>
    );
};

const MarketStat = ({ label, value, border }: { label: string; value: string; border?: boolean }) => (
    <div className={cn('text-center', border && 'border-x border-white/5')}>
        <p className="text-[9px] text-slate-500 uppercase font-bold tracking-widest mb-0.5">{label}</p>
        <p className="text-sm font-bold text-white">{value}</p>
    </div>
);

const FooterStat = ({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) => (
    <div>
        <p className="text-[9px] text-slate-600 uppercase font-bold tracking-widest mb-0.5">{label}</p>
        <p className={cn('text-xs font-mono', highlight ? 'text-blue-400' : 'text-slate-400')}>{value}</p>
    </div>
);
