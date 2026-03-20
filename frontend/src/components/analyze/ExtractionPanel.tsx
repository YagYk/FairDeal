import React from 'react';
import { ContractExtractionResult, ExtractionMethod, ExtractedField } from '../../lib/types';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { cn, formatCurrency } from '../../lib/utils';
import { FileText, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

interface ExtractionPanelProps {
    extraction: ContractExtractionResult;
    compact?: boolean;
}

export const ExtractionPanel = ({ extraction, compact }: ExtractionPanelProps) => {
    const fields = [
        { label: 'Role', field: extraction.role, type: 'text' },
        { label: 'Company', field: extraction.company_type, type: 'text' },
        { label: 'Experience', field: extraction.experience_level, type: 'text' },
        { label: 'Salary (CTC)', field: extraction.ctc_inr, type: 'currency' },
        { label: 'Notice Period', field: extraction.notice_period_days, type: 'days' },
        { label: 'Bond Amount', field: extraction.bond_amount_inr, type: 'currency' },
        { label: 'Non-Compete', field: extraction.non_compete_months, type: 'months' },
        { label: 'Probation', field: extraction.probation_months, type: 'months' },
    ];

    return (
        <Card className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden">
            <CardHeader className="pb-4 border-b border-white/5">
                <CardTitle className="flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                    <FileText className="h-5 w-5 text-gold" />
                    <span>Extracted Terms</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
                <div className="divide-y divide-white/5">
                    {fields.map((item, idx) => (
                        <div key={idx} className={cn("p-4", compact ? "px-4 py-3" : "p-6")}>
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                <div className="space-y-1">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{item.label}</span>
                                        <ConfidenceBadge confidence={item.field?.confidence || 0} />
                                        <MethodBadge method={item.field?.method || ExtractionMethod.MISSING} />
                                    </div>
                                    <p className="text-lg font-bold text-white">
                                        {item.type === 'currency' ? formatCurrency(item.field?.value) :
                                            item.type === 'days' ? (item.field?.value ? `${item.field.value} Days` : 'N/A') :
                                                item.type === 'months' ? (item.field?.value ? `${item.field.value} Months` : 'N/A') :
                                                    item.field?.value || 'Not found'}
                                    </p>
                                </div>

                                {item.field?.source_text && !compact && (
                                    <div className="flex-1 max-w-md">
                                        <div className="rounded-lg bg-white/5 p-3 border border-white/5 relative group">
                                            <span className="absolute -top-2 left-3 bg-[#0a0a0a] px-1 text-[10px] font-bold text-slate-500 border border-white/10 rounded">
                                                SOURCE {item.field.page_number ? `P. ${item.field.page_number}` : ''}
                                            </span>
                                            <p className="text-xs font-mono text-slate-400 line-clamp-2 italic">
                                                "{item.field.source_text}"
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};

const ConfidenceBadge = ({ confidence }: { confidence: number }) => {
    if (confidence >= 0.9) return <Badge variant="success" className="text-[10px] h-4">High Conf</Badge>;
    if (confidence >= 0.6) return <Badge variant="warning" className="text-[10px] h-4">Med Conf</Badge>;
    if (confidence > 0) return <Badge variant="error" className="text-[10px] h-4">Low Conf</Badge>;
    return null;
};

const MethodBadge = ({ method }: { method: ExtractionMethod }) => {
    const styles = {
        [ExtractionMethod.REGEX]: { label: 'Regex', icon: CheckCircle2, class: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
        [ExtractionMethod.SNIPER_LLM]: { label: 'Sniper LLM', icon: FileText, class: 'bg-blue-500/10 text-blue-400 border-blue-500/20' },
        [ExtractionMethod.LLM_FALLBACK]: { label: 'LLM Fallback', icon: AlertTriangle, class: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
        [ExtractionMethod.MISSING]: { label: 'Missing', icon: HelpCircle, class: 'bg-white/5 text-slate-500 border-white/10' },
    };

    const config = styles[method] || styles[ExtractionMethod.MISSING];

    return (
        <div className={cn("inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-bold border tracking-tight uppercase", config.class)}>
            <config.icon className="h-2.5 w-2.5 mr-1" />
            {config.label}
        </div>
    );
};
