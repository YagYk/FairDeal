import React from 'react';
import { KBStats } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface KBStatsCardProps {
    stats?: KBStats;
    isLoading: boolean;
}

export const KBStatsCard = ({ stats, isLoading }: KBStatsCardProps) => {
    const data = React.useMemo(() => {
        if (!stats || !stats.clause_type_counts) return [];
        return Object.entries(stats.clause_type_counts).map(([name, value]) => ({
            name: name.toUpperCase(),
            value,
        }));
    }, [stats]);

    const COLORS = ['#D4AF37', '#FFBF00', '#B8860B', '#CAA472', '#8B7355', '#4A4A4A'];

    return (
        <Card className="border-white/5 bg-white/5 backdrop-blur-xl group">
            <CardHeader className="border-b border-white/5">
                <CardTitle className="text-xs font-black text-slate-500 uppercase tracking-[0.2em] leading-tight group-hover:text-gold transition-colors">Clause Distribution</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
                {isLoading ? (
                    <div className="h-64 w-full animate-pulse bg-white/5 rounded-2xl" />
                ) : (
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={data}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {data.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#050505', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '10px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Legend
                                    layout="vertical"
                                    align="right"
                                    verticalAlign="middle"
                                    iconType="circle"
                                    formatter={(value) => <span className="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{value}</span>}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};
