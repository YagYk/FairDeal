import React from 'react';
import { KBChunkPreview } from '../../lib/types';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Copy, ChevronRight } from 'lucide-react';
import { Button } from '../ui/Button';
import { formatPercent } from '../../lib/utils';
import { cn } from '../../lib/utils';

interface ChunkViewerProps {
    chunk: KBChunkPreview;
    index?: number;
}

export const ChunkViewer = ({ chunk, index }: ChunkViewerProps) => {
    const [copied, setCopied] = React.useState(false);

    const copyText = () => {
        navigator.clipboard.writeText(chunk.text_preview);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <Card className="group relative border-white/5 bg-white/5 backdrop-blur-xl hover:border-gold/30 transition-all duration-500 rounded-3xl overflow-hidden">
            <div className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
            <CardContent className="p-6 relative z-10">
                <div className="flex items-center justify-between mb-5 border-b border-white/5 pb-3">
                    <div className="flex items-center space-x-3">
                        {index !== undefined && <span className="text-[10px] font-black text-slate-600 font-mono tracking-tighter">NODE_{String(index + 1).padStart(3, '0')}</span>}
                        <Badge variant="outline" className="uppercase tracking-[0.2em] text-[10px] h-5 rounded-md px-2 border-gold/20 bg-gold/5 text-gold">
                            {chunk.clause_type}
                        </Badge>
                        {chunk.similarity !== undefined && (
                            <Badge variant="secondary" className="text-[10px] h-5 rounded-md px-2 font-mono">
                                SIMILARITY: {formatPercent(chunk.similarity * 100)}
                            </Badge>
                        )}
                    </div>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={copyText}
                        className={cn("h-8 px-4 text-[10px] uppercase font-black tracking-widest rounded-xl hover:bg-white/10 transition-all border border-white/10", copied ? "text-gold bg-gold/10 border-gold/30" : "text-slate-500")}
                    >
                        <Copy className="h-3 w-3 mr-2" />
                        {copied ? 'Captured' : 'Capture Segment'}
                    </Button>
                </div>
                <div className="relative">
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-white/5 rounded-full group-hover:bg-gold transition-colors duration-500" />
                    <p className="pl-6 text-sm text-slate-300 leading-relaxed font-mono whitespace-pre-wrap line-clamp-10 selection:bg-gold/30 selection:text-white">
                        {chunk.text_preview}
                    </p>
                </div>
                <div className="mt-5 flex items-center justify-between text-[10px] font-black text-slate-600 uppercase tracking-[0.2em]">
                    <div className="flex items-center gap-2">
                        <ChevronRight className="h-3 w-3 text-gold" />
                        <span>Source UID: <span className="text-slate-400 font-mono">{chunk.chunk_id.substring(0, 16)}</span></span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
