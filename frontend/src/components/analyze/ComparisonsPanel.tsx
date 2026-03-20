import React from 'react';
import { PercentileResult } from '../../lib/types';
import { Card } from '../ui/Card';
import { ArrowLeft, ArrowRight, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface ComparisonsPanelProps {
    salaryPercentile?: PercentileResult;
    noticePercentile?: PercentileResult;
}

export const ComparisonsPanel = ({ salaryPercentile, noticePercentile }: ComparisonsPanelProps) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ComparisonCard
                title="Salary Competitiveness"
                percentile={salaryPercentile}
                type="salary"
            />
            <ComparisonCard
                title="Notice Period Favorable"
                percentile={noticePercentile}
                type="notice"
            />
        </div>
    );
};

const ComparisonCard = ({ title, percentile, type }: {
    title: string,
    percentile?: PercentileResult,
    type: 'salary' | 'notice'
}) => {
    if (!percentile) return null;

    const isGood = type === 'salary' ? percentile.value >= 60 : percentile.value <= 40;
    const isBad = type === 'salary' ? percentile.value <= 40 : percentile.value >= 60;

    return (
        <Card className="p-6 border-white/5 bg-white/5 backdrop-blur-xl relative overflow-hidden group">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest">{title}</h4>
                    <div className="flex items-baseline space-x-2 mt-1">
                        <span className="text-2xl font-black text-white">{percentile.field_display}</span>
                        <span className="text-sm text-slate-500 font-medium">
                            {type === 'salary' ? 'CTC' : 'Notice'}
                        </span>
                    </div>
                </div>
                <div className={`
                    rounded-full p-2 
                    ${isGood ? 'bg-emerald-500/10 text-emerald-400' : isBad ? 'bg-red-500/10 text-red-400' : 'bg-amber-500/10 text-amber-400'}
                `}>
                    {isGood ? <TrendingUp size={16} /> : isBad ? <TrendingDown size={16} /> : <Minus size={16} />}
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <div className="flex justify-between text-xs mb-1.5 font-medium">
                        <span className="text-slate-500">Market Percentile</span>
                        <span className="text-white">{percentile.value.toFixed(0)}th percentile</span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-1000 ease-out ${isGood ? 'bg-emerald-500/50' : isBad ? 'bg-red-500/50' : 'bg-amber-500/50'
                                }`}
                            style={{ width: `${percentile.value}%` }}
                        />
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-600 mt-1 font-mono">
                        <span>Low</span>
                        <span>Median</span>
                        <span>High</span>
                    </div>
                </div>

                <div className="text-xs text-slate-400 leading-relaxed p-3 bg-white/5 rounded-lg border border-white/5">
                    <span className="font-bold block mb-1 text-slate-300">Interpretation:</span>
                    {percentile.insight}
                </div>
            </div>
        </Card>
    );
};
