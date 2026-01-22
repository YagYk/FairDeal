import React from 'react';
import { KBContractMetadata } from '../../lib/types';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../ui/Table';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { Eye, ChevronLeft, ChevronRight, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ContractsTableProps {
    contracts: KBContractMetadata[];
    isLoading: boolean;
    onPageChange: (offset: number) => void;
    offset: number;
    limit: number;
    total: number;
}

export const ContractsTable = ({ contracts, isLoading, onPageChange, offset, limit, total }: ContractsTableProps) => {
    const navigate = useNavigate();

    return (
        <div className="space-y-6">
            <div className="rounded-3xl border border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden shadow-2xl">
                <Table>
                    <TableHeader>
                        <TableRow className="border-white/10 hover:bg-transparent">
                            <TableHead className="w-12">#</TableHead>
                            <TableHead>Contract ID</TableHead>
                            <TableHead>Filename</TableHead>
                            <TableHead>Entities / Meta</TableHead>
                            <TableHead>Chunks</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            Array.from({ length: 5 }).map((_, i) => (
                                <TableRow key={i}>
                                    <TableCell colSpan={6}>
                                        <div className="h-6 w-full animate-pulse bg-white/5 rounded" />
                                    </TableCell>
                                </TableRow>
                            ))
                        ) : contracts.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="h-32 text-center text-slate-500">
                                    No contracts found in the Knowledge Base.
                                </TableCell>
                            </TableRow>
                        ) : (
                            contracts.map((c, i) => (
                                <TableRow key={c.contract_id} className="group transition-colors duration-300">
                                    <TableCell className="text-slate-500 font-mono text-xs">{offset + i + 1}</TableCell>
                                    <TableCell className="font-mono text-[10px] font-bold text-slate-400 group-hover:text-white transition-colors">
                                        {c.contract_id.substring(0, 12)}
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex items-center space-x-3">
                                            <div className="h-8 w-8 rounded-lg bg-gold/10 flex items-center justify-center border border-gold/20">
                                                <FileText className="h-4 w-4 text-gold" />
                                            </div>
                                            <span className="font-bold text-white tracking-tight">{c.filename}</span>
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <div className="flex flex-wrap gap-1.5">
                                            {c.company_type && (
                                                <Badge variant="secondary" className="text-[10px] h-5 rounded-md px-2">
                                                    {c.company_type}
                                                </Badge>
                                            )}
                                            {c.role && (
                                                <Badge variant="outline" className="text-[10px] h-5 rounded-md px-2">
                                                    {c.role}
                                                </Badge>
                                            )}
                                        </div>
                                    </TableCell>
                                    <TableCell>
                                        <span className="text-xs font-black text-slate-400 group-hover:text-gold transition-colors">{c.extra?.num_chunks || 0}</span>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => navigate(`/kb/contracts/${c.contract_id}`)}
                                            className="text-slate-400 hover:text-gold hover:bg-gold/10 rounded-xl"
                                        >
                                            <Eye className="h-4 w-4 mr-2" />
                                            View
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>

            <div className="flex items-center justify-between px-2">
                <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em]">
                    Showing {Math.min(total, offset + 1)}-{Math.min(total, offset + contracts.length)} OF {total}
                </p>
                <div className="flex items-center space-x-3">
                    <Button
                        variant="ghost"
                        size="sm"
                        disabled={offset === 0 || isLoading}
                        onClick={() => onPageChange(Math.max(0, offset - limit))}
                        className="text-slate-400 hover:text-white hover:bg-white/5 rounded-xl border border-white/5"
                    >
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        Prev
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        disabled={offset + contracts.length >= total || isLoading}
                        onClick={() => onPageChange(offset + limit)}
                        className="text-slate-400 hover:text-white hover:bg-white/5 rounded-xl border border-white/5"
                    >
                        Next
                        <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                </div>
            </div>
        </div>
    );
};
