import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { BenchmarkResult } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { formatCurrency, formatPercent } from '../../lib/utils';
import { BarChart3, Info, Users, Filter } from 'lucide-react';

interface BenchmarkPanelProps {
    benchmark?: BenchmarkResult;
    userSalary?: number;
}

export const BenchmarkPanel = ({ benchmark, userSalary }: BenchmarkPanelProps) => {
    if (!benchmark) {
        return (
            <Card className="shadow-premium border-none ring-1 ring-slate-200 bg-slate-50/50">
                <CardContent className="p-12 text-center">
                    <Info className="h-10 w-10 text-slate-300 mx-auto mb-4" />
                    <h3 className="text-lg font-bold text-slate-800">No benchmark available</h3>
                    <p className="text-sm text-slate-500">We couldn't find a matching cohort for this role and experience level.</p>
                </CardContent>
            </Card>
        );
    }

    // Generate synthetic distribution data based on P25, Median, P75
    const data = generateDistributionData(benchmark);

    return (
        <Card className="shadow-premium border-none ring-1 ring-slate-200">
            <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center space-x-2">
                        <BarChart3 className="h-5 w-5 text-brand-500" />
                        <span>Market Benchmarking</span>
                    </CardTitle>
                    <div className="flex items-center space-x-2">
                        <Badge variant="secondary" className="font-mono">
                            <Users className="h-3 w-3 mr-1" />
                            N={benchmark.cohort_size}
                        </Badge>
                    </div>
                </div>
                <CardDescription>
                    Your salary vs. peer cohort in {benchmark.filters_used.company_type || 'selected industry'}.
                </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2">
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={data}>
                                    <defs>
                                        <linearGradient id="colorSal" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#4a6cf7" stopOpacity={0.1} />
                                            <stop offset="95%" stopColor="#4a6cf7" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis
                                        dataKey="salary"
                                        hide
                                    />
                                    <YAxis hide />
                                    <Tooltip
                                        content={({ active, payload }) => {
                                            if (active && payload && payload.length) {
                                                return (
                                                    <div className="rounded-lg bg-slate-900 px-3 py-2 text-xs text-white shadow-xl">
                                                        <p className="font-bold">{formatCurrency(payload[0].payload.salary)}</p>
                                                        <p className="text-slate-400">Frequency density</p>
                                                    </div>
                                                );
                                            }
                                            return null;
                                        }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="density"
                                        stroke="#4a6cf7"
                                        strokeWidth={2}
                                        fillOpacity={1}
                                        fill="url(#colorSal)"
                                    />
                                    {userSalary && (
                                        <ReferenceLine
                                            x={findClosestX(data, userSalary)}
                                            stroke="#0f172a"
                                            strokeWidth={2}
                                            label={{
                                                value: 'YOU',
                                                position: 'top',
                                                fill: '#0f172a',
                                                fontSize: 10,
                                                fontWeight: 'bold'
                                            }}
                                        />
                                    )}
                                    <ReferenceLine
                                        x={findClosestX(data, benchmark.market_median)}
                                        stroke="#94a3b8"
                                        strokeDasharray="3 3"
                                        label={{ value: 'MEDIAN', position: 'insideTopLeft', fill: '#94a3b8', fontSize: 9 }}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>

                        <div className="mt-4 flex justify-between px-2 text-[10px] font-bold text-slate-400 tracking-tighter uppercase">
                            <span>Low (P25)</span>
                            <span>Median</span>
                            <span>High (P75)</span>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="rounded-2xl bg-brand-50/50 p-6 border border-brand-100 flex flex-col items-center text-center">
                            <span className="text-xs font-bold text-brand-600 uppercase tracking-widest mb-1">Percentile</span>
                            <span className="text-5xl font-black text-brand-700">{Math.round(benchmark.percentile_salary || 0)}</span>
                            <p className="text-xs text-brand-600 mt-2 font-medium">
                                You earn more than {Math.round(benchmark.percentile_salary || 0)}% of the market.
                            </p>
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center space-x-2 text-slate-500">
                                <Filter className="h-3.5 w-3.5" />
                                <span className="text-[10px] font-bold uppercase tracking-widest">Filters Used</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {Object.entries(benchmark.filters_used).map(([key, val]) => (
                                    <Badge key={key} variant="outline" className="text-[10px] lowercase">
                                        {key}: {val}
                                    </Badge>
                                ))}
                            </div>
                            {benchmark.broaden_steps.length > 0 && (
                                <div className="rounded-lg bg-amber-50 p-3 border border-amber-100">
                                    <p className="text-[10px] font-bold text-amber-600 uppercase mb-1">Broadening</p>
                                    <ul className="text-[10px] text-amber-700 space-y-0.5">
                                        {benchmark.broaden_steps.map((step, i) => (
                                            <li key={i}>• {step.replace(/_/g, ' ')}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

// Helper to generate a normal distribution curve
function generateDistributionData(benchmark: BenchmarkResult) {
    const { market_p25, market_median, market_p75 } = benchmark;
    const stdDev = (market_p75 - market_p25) / 1.35; // Rough approximation
    const points = 50;
    const start = market_p25 - stdDev;
    const end = market_p75 + stdDev;
    const step = (end - start) / points;

    const data = [];
    for (let i = 0; i <= points; i++) {
        const x = start + i * step;
        // Normal distribution formula
        const density = (1 / (stdDev * Math.sqrt(2 * Math.PI))) *
            Math.exp(-0.5 * Math.pow((x - market_median) / stdDev, 2));
        data.push({
            salary: x,
            density: density * 1000000, // Scaling for Recharts
        });
    }
    return data;
}

function findClosestX(data: any[], target: number) {
    return data.reduce((prev, curr) =>
        Math.abs(curr.salary - target) < Math.abs(prev.salary - target) ? curr : prev
    ).salary;
}
