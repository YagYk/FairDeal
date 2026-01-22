import React from 'react';
import { KBHealth } from '../../lib/types';
import { Card, CardContent } from '../ui/Card';
import { Activity, Database, Server, HardDrive } from 'lucide-react';
import { cn } from '../../lib/utils';

interface HealthPanelProps {
    health?: KBHealth;
    isLoading: boolean;
}

export const HealthPanel = ({ health, isLoading }: HealthPanelProps) => {
    const stats = [
        { label: 'Chroma Path', value: health?.chroma_path || 'Not connected', icon: Database },
        { label: 'Files Processed', value: health?.processed_count || 0, icon: HardDrive },
        { label: 'Collection Size', value: health?.collection_count || 0, icon: Server },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {stats.map((stat, i) => (
                <Card key={i} className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden group hover:border-gold/30 transition-all duration-300">
                    <CardContent className="p-5 flex items-center space-x-5">
                        <div className="h-12 w-12 rounded-2xl bg-gold/10 flex items-center justify-center text-gold border border-gold/20 shadow-[0_0_15px_rgba(212,175,55,0.1)]">
                            <stat.icon className="h-6 w-6" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] leading-tight mb-1">{stat.label}</p>
                            <p className="text-base font-bold text-white truncate tracking-tight">
                                {isLoading ? '...' : stat.value}
                            </p>
                        </div>
                        {!isLoading && (
                            <div className="h-2 w-2 rounded-full bg-gold shadow-[0_0_10px_rgba(212,175,55,0.8)] animate-pulse" />
                        )}
                    </CardContent>
                </Card>
            ))}
        </div>
    );
};
