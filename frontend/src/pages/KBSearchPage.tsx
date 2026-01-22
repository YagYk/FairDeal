import React, { useState } from 'react';
import { useKBSearch } from '../lib/api';
import { ClauseType } from '../lib/types';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { Search, SlidersHorizontal, Layers } from 'lucide-react';
import { ChunkViewer } from '../components/kb/ChunkViewer';

export const KBSearchPage = () => {
    const [query, setQuery] = useState('');
    const [clauseType, setClauseType] = useState<ClauseType | undefined>(undefined);
    const [topK, setTopK] = useState(5);
    const [searchTrigger, setSearchTrigger] = useState('');

    const { data: results = [], isLoading } = useKBSearch({
        query: searchTrigger,
        clause_type: clauseType,
        top_k: topK,
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setSearchTrigger(query);
    };

    return (
        <div className="space-y-10 pb-20">
            <div>
                <h1 className="text-4xl font-serif font-bold text-white tracking-tight">Discovery Engine</h1>
                <p className="text-slate-400 mt-2 font-medium">Semantic search across the Knowledge Base repository.</p>
            </div>

            <Card className="border-white/5 bg-white/5 backdrop-blur-xl group overflow-hidden">
                <div className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <CardContent className="pt-8 relative z-10">
                    <form onSubmit={handleSearch} className="space-y-8">
                        <div className="relative group/input">
                            <Search className="absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-500 group-focus-within/input:text-gold transition-colors" />
                            <input
                                placeholder="Inquire about specific clause language (e.g. 'unlimited non-compete')..."
                                className="w-full h-14 bg-white/5 border border-white/10 rounded-2xl pl-14 pr-32 text-white focus:border-gold/30 focus:ring-1 focus:ring-gold/30 transition-all outline-none placeholder:text-slate-600"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                            />
                            <Button
                                type="submit"
                                className="absolute right-2 top-2 h-10 px-8 rounded-xl bg-gold text-charcoal hover:bg-gold-light font-black uppercase text-[10px] tracking-widest shadow-[0_0_20px_rgba(212,175,55,0.2)]"
                                loading={isLoading}
                            >
                                Initiate Search
                            </Button>
                        </div>

                        <div className="flex flex-wrap items-center gap-10 pt-2 border-t border-white/5 px-2">
                            <div className="flex items-center space-x-3 text-slate-500">
                                <SlidersHorizontal className="h-4 w-4" />
                                <span className="text-[10px] font-black uppercase tracking-[0.2em] mb-0.5">Engine Parameters</span>
                            </div>

                            <div className="w-64">
                                <select
                                    value={clauseType || ''}
                                    onChange={(e) => setClauseType(e.target.value as ClauseType || undefined)}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white focus:border-gold/30 transition-all outline-none appearance-none cursor-pointer"
                                >
                                    <option value="" className="bg-[#121212]">Global Clause Search</option>
                                    {Object.values(ClauseType).map((t) => (
                                        <option key={t} value={t} className="bg-[#121212]">{t.toUpperCase()}</option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex items-center space-x-6 flex-1 max-w-sm">
                                <span className="text-[10px] font-black text-gold uppercase tracking-[0.2em] whitespace-nowrap pt-0.5">Node Limit: {topK}</span>
                                <input
                                    type="range"
                                    min="1"
                                    max="20"
                                    value={topK}
                                    onChange={(e) => setTopK(parseInt(e.target.value))}
                                    className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-gold hover:accent-amber transition-all"
                                />
                            </div>
                        </div>
                    </form>
                </CardContent>
            </Card>

            <div className="space-y-8">
                {isLoading ? (
                    <div className="space-y-6">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <div key={i} className="h-40 w-full animate-pulse bg-white/5 rounded-3xl" />
                        ))}
                    </div>
                ) : results.length > 0 ? (
                    <div className="space-y-6">
                        <div className="flex items-center space-x-3 text-slate-500 mb-2 border-b border-white/5 pb-4">
                            <Layers className="h-4 w-4" />
                            <span className="text-[10px] font-black uppercase tracking-[0.2em]">Semantic Hits Detected ({results.length})</span>
                        </div>
                        {results.map((result, i) => (
                            <ChunkViewer key={`${result.contract_id}-${result.chunk_id}`} chunk={result} index={i} />
                        ))}
                    </div>
                ) : searchTrigger ? (
                    <div className="p-20 text-center rounded-[40px] border border-dashed border-white/10 bg-white/5">
                        <p className="text-slate-500 font-medium">No verified data nodes match the inquiry: <span className="text-gold italic">"{searchTrigger}"</span>.</p>
                    </div>
                ) : (
                    <div className="p-20 text-center text-slate-600 italic font-serif text-lg tracking-tight">
                        Initiate a query above to explore the deterministic knowledge base...
                    </div>
                )}
            </div>
        </div>
    );
};
