import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useKBContract, useKBContractChunks } from '../lib/api';
import { Button } from '../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { ArrowLeft, FileText, Code, List } from 'lucide-react';
import { ChunkViewer } from '../components/kb/ChunkViewer';

export const KBContractPage = () => {
    const { contractId } = useParams<{ contractId: string }>();
    const { data: contract, isLoading: contractLoading } = useKBContract(contractId!);
    const { data: chunks = [], isLoading: chunksLoading } = useKBContractChunks(contractId!);

    return (
        <div className="space-y-8 pb-20">
            <Link to="/kb" className="inline-flex items-center text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 hover:text-gold transition-all group">
                <ArrowLeft className="mr-2 h-4 w-4 group-hover:-translate-x-2 transition-transform" />
                Return to repository
            </Link>

            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-center space-x-5">
                    <div className="h-14 w-14 rounded-2xl bg-gold/10 text-gold flex items-center justify-center border border-gold/20 shadow-[0_0_20px_rgba(212,175,55,0.1)]">
                        <FileText className="h-7 w-7" />
                    </div>
                    <div>
                        <h1 className="text-4xl font-serif font-bold text-white tracking-tight">Contract Intelligence</h1>
                        <p className="font-mono text-[10px] text-gold mt-1 uppercase tracking-[0.3em] opacity-70">{contractId}</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                <div className="lg:col-span-4 space-y-6">
                    <Card className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden group">
                        <CardHeader className="border-b border-white/5 bg-white/5">
                            <CardTitle className="flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500 group-hover:text-gold transition-colors">
                                <Code className="h-4 w-4" />
                                <span>Deterministic Schema</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="p-0 bg-[#050505]">
                            <div className="p-6">
                                <pre className="text-[11px] text-amber/80 font-mono overflow-auto max-h-[500px] scrollbar-thin scrollbar-thumb-gold/20 leading-relaxed">
                                    {JSON.stringify(contract, null, 2)}
                                </pre>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                <div className="lg:col-span-8 space-y-8">
                    <div className="flex items-center justify-between border-b border-white/5 pb-4">
                        <h2 className="text-xl font-bold text-white flex items-center space-x-3">
                            <List className="h-5 w-5 text-gold" />
                            <span className="tracking-tight">Verified Contract Segments <span className="text-slate-500 font-medium ml-2 text-sm italic">({chunks.length} nodes)</span></span>
                        </h2>
                    </div>

                    <div className="space-y-4">
                        {chunksLoading ? (
                            Array.from({ length: 3 }).map((_, i) => (
                                <div key={i} className="h-32 w-full animate-pulse bg-slate-100 rounded-xl" />
                            ))
                        ) : chunks.map((chunk, i) => (
                            <ChunkViewer key={chunk.chunk_id} chunk={chunk} index={i} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
