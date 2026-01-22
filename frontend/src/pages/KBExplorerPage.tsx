import React, { useState } from 'react';
import { HealthPanel } from '../components/kb/HealthPanel';
import { KBStatsCard } from '../components/kb/KBStatsCard';
import { ContractsTable } from '../components/kb/ContractsTable';
import { useKBHealth, useKBStats, useKBContracts } from '../lib/api';

export const KBExplorerPage = () => {
    const [offset, setOffset] = useState(0);
    const limit = 10;

    const { data: health, isLoading: healthLoading } = useKBHealth();
    const { data: stats, isLoading: statsLoading } = useKBStats();
    const { data: contractsResponse, isLoading: contractsLoading } = useKBContracts({ limit, offset });

    const contracts = contractsResponse?.contracts || [];

    return (
        <div className="space-y-8 pb-20">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-serif font-bold text-white tracking-tight">KB Explorer</h1>
                    <p className="text-slate-400 mt-2 font-medium">Internal knowledge base monitoring and document management.</p>
                </div>
            </div>

            <HealthPanel health={health} isLoading={healthLoading} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-1">
                    <KBStatsCard stats={stats} isLoading={statsLoading} />
                </div>
                <div className="lg:col-span-2">
                    <ContractsTable
                        contracts={contracts}
                        total={contractsResponse?.total || 0}
                        isLoading={contractsLoading}
                        offset={offset}
                        limit={limit}
                        onPageChange={setOffset}
                    />
                </div>
            </div>
        </div>
    );
};
