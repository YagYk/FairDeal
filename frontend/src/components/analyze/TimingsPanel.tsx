import React from 'react';
import { Timings } from '../../lib/types';
import { Card, CardContent } from '../ui/Card';
import { formatMs } from '../../lib/utils';
import { Clock } from 'lucide-react';

interface TimingsPanelProps {
    timings: Timings;
}

export const TimingsPanel = ({ timings }: TimingsPanelProps) => {
    const steps = [
        { label: 'Parsing', ms: timings.parse_ms, color: 'bg-blue-400' },
        { label: 'Extraction', ms: timings.extract_ms, color: 'bg-indigo-400' },
        { label: 'Benchmark', ms: timings.benchmark_ms, color: 'bg-cyan-400' },
        { label: 'RAG / Evidence', ms: timings.rag_ms, color: 'bg-brand-400' },
    ];

    const total = timings.total_ms || steps.reduce((acc, s) => acc + s.ms, 0);

    return (
        <Card className="shadow-sm border-none ring-1 ring-slate-100 bg-slate-50/50">
            <CardContent className="p-4">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2 text-slate-500">
                        <Clock className="h-4 w-4" />
                        <span className="text-xs font-bold uppercase tracking-widest">Processing Latency</span>
                    </div>
                    <span className="text-sm font-bold text-slate-900">{formatMs(total)}</span>
                </div>

                <div className="flex h-2 w-full overflow-hidden rounded-full bg-slate-200">
                    {steps.map((step, i) => (
                        <div
                            key={i}
                            style={{ width: `${(step.ms / total) * 100}%` }}
                            className={step.color}
                            title={`${step.label}: ${formatMs(step.ms)}`}
                        />
                    ))}
                </div>

                <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                    {steps.map((step, i) => (
                        <div key={i} className="flex flex-col">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{step.label}</span>
                            <span className="text-sm font-semibold text-slate-700">{formatMs(step.ms)}</span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};
