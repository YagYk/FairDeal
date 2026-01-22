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
        <Card className="p-6 border-none ring-1 ring-slate-200 shadow-sm relative overflow-hidden group">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest">{title}</h4>
                    <div className="flex items-baseline space-x-2 mt-1">
                        <span className="text-2xl font-black text-slate-900">{percentile.field_display}</span>
                        <span className="text-sm text-slate-500 font-medium">
                            {type === 'salary' ? 'CTC' : 'Notice'}
                        </span>
                    </div>
                </div>
                <div className={`
                    rounded-full p-2 
                    ${isGood ? 'bg-emerald-100 text-emerald-600' : isBad ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'}
                `}>
                    {isGood ? <TrendingUp size={16} /> : isBad ? <TrendingDown size={16} /> : <Minus size={16} />}
                </div>
            </div>

            <div className="space-y-4">
                <div>
                    <div className="flex justify-between text-xs mb-1.5 font-medium">
                        <span className="text-slate-500">Market Percentile</span>
                        <span className="text-slate-900">{percentile.value.toFixed(0)}th percentile</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-1000 ease-out ${isGood ? 'bg-emerald-500' : isBad ? 'bg-red-500' : 'bg-amber-500'
                                }`}
                            style={{ width: `${percentile.value}%` }}
                        />
                    </div>
                    <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
                        <span>Low</span>
                        <span>Median</span>
                        <span>High</span>
                    </div>
                </div>

                <div className="text-xs text-slate-600 leading-relaxed p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="font-semibold block mb-1">Interpretation:</span>
                    {percentile.insight}
                </div>
            </div>

            {/* Background decoration */}
            <div className="absolute -right-6 -bottom-6 opacity-5 pointer-events-none">
                <div className="w-24 h-24 rounded-full bg-current text-slate-900" />
            </div>
        </Card>
    );
};
