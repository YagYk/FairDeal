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
        <Card className="shadow-premium border-none ring-1 ring-slate-200">
            <CardHeader className="border-b">
                <CardTitle className="flex items-center space-x-2">
                    <Database className="h-5 w-5 text-brand-500" />
                    <span>Knowledge Base Evidence</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                {clauseTypes.length === 0 ? (
                    <div className="p-12 text-center">
                        <p className="text-sm text-slate-500">No matching evidence found in the Knowledge Base.</p>
                    </div>
                ) : (
                    <div className="divide-y divide-slate-100">
                        {clauseTypes.map(([clauseType, chunks]) => (
                            <div key={clauseType} className="p-6">
                                <div className="flex items-center space-x-2 mb-4">
                                    <Badge variant="info" className="uppercase tracking-widest px-1.5 h-5 text-[10px]">
                                        {clauseType}
                                    </Badge>
                                    <span className="text-[10px] font-bold text-slate-400">
                                        {chunks.length} SIMILAR CLAUSES FOUND
                                    </span>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {chunks.map((chunk, idx) => (
                                        <div key={idx} className="group relative rounded-xl border border-slate-100 bg-slate-50/50 p-4 transition-all hover:bg-white hover:border-brand-200 hover:shadow-md">
                                            <div className="flex items-center justify-between mb-2">
                                                <Badge variant="secondary" className="font-mono text-[9px] h-4 bg-slate-200/50">
                                                    Match: {formatPercent(chunk.similarity * 100)}
                                                </Badge>
                                                <Link
                                                    to={`/kb/contracts/${chunk.contract_id}`}
                                                    className="text-slate-400 hover:text-brand-500 transition-colors"
                                                >
                                                    <ExternalLink className="h-3 w-3" />
                                                </Link>
                                            </div>
                                            <p className="text-xs text-slate-600 line-clamp-3 italic mb-3">
                                                "{chunk.text_preview}..."
                                            </p>
                                            <div className="flex items-center justify-between text-[9px] font-bold text-slate-400 uppercase tracking-tighter">
                                                <span>CID: {chunk.contract_id.substring(0, 8)}</span>
                                                <div className="flex items-center text-brand-500">
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
