import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import { Shield, AlertTriangle, CheckCircle, HelpCircle } from 'lucide-react';

interface ClauseData {
    label: string;
    status: 'safe' | 'caution' | 'risk' | 'danger' | 'unknown';
    detail: string;
    impact: number; // 0-100, higher = safer
}

interface ClauseHeatmapProps {
    clauses: ClauseData[];
}

const STATUS_CONFIG = {
    safe: { color: 'bg-emerald-500', border: 'border-emerald-500/30', text: 'text-emerald-400', glow: 'bg-emerald-500', label: 'Safe', icon: CheckCircle },
    caution: { color: 'bg-amber-500', border: 'border-amber-500/30', text: 'text-amber-400', glow: 'bg-amber-500', label: 'Caution', icon: AlertTriangle },
    risk: { color: 'bg-orange-500', border: 'border-orange-500/30', text: 'text-orange-400', glow: 'bg-orange-500', label: 'Risk', icon: AlertTriangle },
    danger: { color: 'bg-red-500', border: 'border-red-500/30', text: 'text-red-400', glow: 'bg-red-500', label: 'Danger', icon: Shield },
    unknown: { color: 'bg-slate-500', border: 'border-slate-500/20', text: 'text-slate-500', glow: 'bg-slate-500', label: 'N/A', icon: HelpCircle },
};

export const ClauseHeatmap = ({ clauses }: ClauseHeatmapProps) => {
    // Compute overall risk score from clauses (excluding unknowns)
    const knownClauses = clauses.filter(c => c.status !== 'unknown');
    const overallScore = knownClauses.length > 0
        ? Math.round(knownClauses.reduce((sum, c) => sum + c.impact, 0) / knownClauses.length)
        : 0;

    const overallStatus = overallScore >= 80 ? 'safe' : overallScore >= 60 ? 'caution' : overallScore >= 40 ? 'risk' : 'danger';
    const overallConfig = STATUS_CONFIG[overallStatus];

    return (
        <div className="space-y-4">
            {/* Overall Score Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em]">Risk Heatmap</h4>
                    <p className="text-[10px] text-slate-600 mt-0.5">{knownClauses.length} clauses analyzed</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className={cn("w-2 h-2 rounded-full", overallConfig.color)} />
                    <span className={cn("text-xl font-serif font-bold", overallConfig.text)}>{overallScore}</span>
                    <span className="text-xs text-slate-600">/100</span>
                </div>
            </div>

            {/* Clause Grid */}
            <div className="space-y-2.5">
                {clauses.map((clause, idx) => {
                    const cfg = STATUS_CONFIG[clause.status];
                    return (
                        <motion.div
                            key={clause.label}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.06 }}
                            className={cn(
                                "relative rounded-lg border p-3 flex items-center gap-3 overflow-hidden",
                                "bg-white/[0.02]", cfg.border
                            )}
                        >
                            {/* Risk bar (background fill showing impact) */}
                            <div
                                className={cn("absolute inset-0 opacity-[0.06]", cfg.color)}
                                style={{ width: `${clause.impact}%` }}
                            />

                            {/* Status dot */}
                            <div className={cn("w-2 h-2 rounded-full shrink-0 z-10", cfg.color)} />

                            {/* Label + Detail */}
                            <div className="flex-1 min-w-0 z-10">
                                <div className="flex items-center justify-between">
                                    <span className="text-[11px] font-semibold text-white/90 truncate">
                                        {clause.label}
                                    </span>
                                    <span className={cn("text-[10px] font-bold font-mono ml-2 shrink-0", cfg.text)}>
                                        {clause.status === 'unknown' ? '—' : clause.impact}
                                    </span>
                                </div>
                                <p className="text-[9px] text-slate-500 truncate mt-0.5">{clause.detail}</p>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
};
