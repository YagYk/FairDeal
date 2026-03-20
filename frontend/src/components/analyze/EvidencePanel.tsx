import React from 'react';
import { EvidenceChunk, ClauseType } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Link } from 'react-router-dom';
import { Database, ExternalLink, ChevronRight } from 'lucide-react';
import { cn, formatPercent } from '../../lib/utils';

interface EvidencePanelProps {
    evidenceByClause: Record<string, EvidenceChunk[]>;
}

export const EvidencePanel = ({ evidenceByClause }: EvidencePanelProps) => {
    const clauseTypes = Object.entries(evidenceByClause).filter(([_, chunks]) => chunks.length > 0);

    return (
        <Card className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden">
            <CardHeader className="border-b border-white/5">
                <CardTitle className="flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                    <Database className="h-5 w-5 text-gold" />
                    <span>Knowledge Base Evidence</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                {clauseTypes.length === 0 ? (
                    <div className="p-12 text-center">
                        <p className="text-sm text-slate-500">No matching evidence found in the Knowledge Base.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-white/5">
                        {clauseTypes.map(([clauseType, chunks]) => (
                            <div key={clauseType} className="p-6">
                                <div className="flex items-center space-x-2 mb-4">
                                    <Badge variant="info" className="uppercase tracking-widest px-1.5 h-5 text-[10px]">
                                        {clauseType}
                                    </Badge>
                                    <span className="text-[10px] font-bold text-slate-500">
                                        {chunks.length} SIMILAR CLAUSES FOUND
                                    </span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {chunks.map((chunk, idx) => (
                                        <div key={idx} className="group relative rounded-xl border border-white/5 bg-white/5 p-4 transition-all hover:bg-white/10 hover:border-gold/20">
                                            <div className="flex items-center justify-between mb-2">
                                                <Badge variant="secondary" className="font-mono text-[9px] h-4">
                                                    Match: {formatPercent(chunk.similarity * 100)}
                                                </Badge>
                                                <Link
                                                    to={`/kb/contracts/${chunk.contract_id}`}
                                                    className="text-slate-500 hover:text-gold transition-colors"
                                                >
                                                    <ExternalLink className="h-3 w-3" />
                                                </Link>
                                            </div>
                                            <p className="text-xs text-slate-400 line-clamp-3 italic mb-3">
                                                "{chunk.text_preview}..."
                                            </p>
                                            <div className="flex items-center justify-between text-[9px] font-bold text-slate-500 uppercase tracking-tighter">
                                                <span>CID: {chunk.contract_id.substring(0, 8)}</span>
                                                <div className="flex items-center text-gold">
                                                    <span>View in KB</span>
                                                    <ChevronRight className="h-2.5 w-2.5 ml-0.5" />
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
};
