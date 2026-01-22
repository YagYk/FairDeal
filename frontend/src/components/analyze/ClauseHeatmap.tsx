import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface ClauseHeatmapProps {
    score: number;
    label: string;
    clauses: {
        type: string;
        risk: 'low' | 'medium' | 'high';
        score: number;
    }[];
}

export const ClauseHeatmap = ({ score, clauses }: ClauseHeatmapProps) => {
    return (
        <div className="space-y-4">
            <div className="flex justify-between items-end mb-2">
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em]">Risk Heatmap</h4>
                <span className="text-2xl font-serif italic text-white">{score}/100</span>
            </div>

            <div className="grid grid-cols-4 gap-2">
                {clauses.map((clause, idx) => (
                    <motion.div
                        key={clause.type}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.1 }}
                        className={cn(
                            "relative aspect-square rounded-xl p-3 flex flex-col justify-between overflow-hidden border",
                            clause.risk === 'low' ? "bg-emerald-500/10 border-emerald-500/20" :
                                clause.risk === 'medium' ? "bg-amber-500/10 border-amber-500/20" :
                                    "bg-red-500/10 border-red-500/20"
                        )}
                    >
                        <div className={cn(
                            "absolute top-0 right-0 w-8 h-8 opacity-20 blur-xl rounded-full",
                            clause.risk === 'low' ? "bg-emerald-500" :
                                clause.risk === 'medium' ? "bg-amber-500" :
                                    "bg-red-500"
                        )} />

                        <span className="text-[8px] font-black uppercase tracking-widest text-slate-500 truncate">
                            {clause.type.replace('_', ' ')}
                        </span>

                        <div className="flex items-baseline gap-1">
                            <span className="text-xl font-serif text-white">{clause.score}</span>
                            <div className={cn(
                                "w-1 h-1 rounded-full",
                                clause.risk === 'low' ? "bg-emerald-400" :
                                    clause.risk === 'medium' ? "bg-amber-400" :
                                        "bg-red-400"
                            )} />
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};
