import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ContextForm } from '../components/analyze/ContextForm';
import { useAnalyzeContract } from '../lib/api';
import { Context, CompanyType } from '../lib/types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import {
    Upload,
    FileText,
    Shield,
    Sparkles,
    TrendingUp,
    Loader2,
    ArrowRight,
    X,
    Cpu,
    Target,
    Zap
} from 'lucide-react';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export const AnalyzePage = () => {
    const navigate = useNavigate();
    const [context, setContext] = useState<Context>(() => {
        const saved = localStorage.getItem('fairdeal_context');
        return saved ? JSON.parse(saved) : {
            role: '',
            experience_level: 1,
            company_type: CompanyType.PRODUCT,
            location: 'national',
            industry: 'tech'
        };
    });
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);

    const analyzeMutation = useAnalyzeContract();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.docx'))) {
            setFile(droppedFile);
        }
    }, []);

    const handleAnalyze = async () => {
        if (!file) return;
        try {
            const data = await analyzeMutation.mutateAsync({ file, context });
            navigate('/results', { state: { result: data } });
        } catch (error) {
            console.error('Analysis failed', error);
        }
    };

    const clearFile = () => {
        setFile(null);
        analyzeMutation.reset();
    };

    return (
        <div className="relative min-h-screen pt-24 pb-12 px-4 overflow-hidden">
            {/* Background elements */}
            <div className="fixed inset-0 animated-grid pointer-events-none opacity-20" />
            <div className="fixed top-1/4 -left-1/4 w-1/2 h-1/2 bg-gold/5 blur-[120px] rounded-full pointer-events-none" />
            <div className="fixed bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-amber/5 blur-[120px] rounded-full pointer-events-none" />

            <div className="relative z-10 w-full max-w-4xl mx-auto space-y-12">
                {/* Header Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center space-y-6"
                >
                    <div className="inline-flex items-center justify-center p-4 rounded-3xl liquid-glass mb-4 group">
                        <Shield className="h-10 w-10 text-gold group-hover:scale-110 transition-transform duration-500" />
                    </div>
                    <h1 className="text-5xl md:text-6xl font-serif font-bold text-white tracking-tight leading-tight">
                        Precision <span className="text-transparent bg-clip-text bg-gradient-to-r from-gold via-amber to-gold">Contract Intelligence</span>
                    </h1>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto font-sans">
                        Unveil the hidden math within your employment contract. High-fidelity benchmarking, red-flag detection, and deterministic scoring.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                    {/* Left Column: Context and Upload */}
                    <div className="lg:col-span-7 space-y-8">
                        {/* Context Card */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.1 }}
                        >
                            <Card className="liquid-glass p-8 border-gold/10">
                                <div className="flex items-center gap-3 mb-6">
                                    <Target className="h-5 w-5 text-gold" />
                                    <h3 className="text-lg font-bold text-gold uppercase tracking-wider">Professional Context</h3>
                                </div>
                                <ContextForm onContextChange={setContext} initialContext={context} />
                            </Card>
                        </motion.div>

                        {/* Dropzone Card */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 }}
                        >
                            <div
                                className={cn(
                                    "relative group rounded-3xl p-1 transition-all duration-500",
                                    isDragging ? "bg-gradient-to-r from-gold to-amber" : "bg-white/5"
                                )}
                                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                                onDragLeave={() => setIsDragging(false)}
                                onDrop={handleDrop}
                            >
                                <div className="bg-[#0a0a0a] rounded-[22px] p-10 border border-white/5 relative overflow-hidden">
                                    <input
                                        type="file"
                                        accept=".pdf,.docx"
                                        onChange={handleFileChange}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                                        disabled={analyzeMutation.isPending}
                                    />

                                    <div className="flex flex-col items-center text-center space-y-6">
                                        <AnimatePresence mode="wait">
                                            {file ? (
                                                <motion.div
                                                    key="file"
                                                    initial={{ scale: 0.8, opacity: 0 }}
                                                    animate={{ scale: 1, opacity: 1 }}
                                                    className="space-y-4"
                                                >
                                                    <div className="h-20 w-20 rounded-2xl bg-gold/10 flex items-center justify-center mx-auto border border-gold/20 shadow-gold-glow">
                                                        <FileText className="h-10 w-10 text-gold" />
                                                    </div>
                                                    <div>
                                                        <p className="text-lg font-bold text-white">{file.name}</p>
                                                        <p className="text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                                                    </div>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); clearFile(); }}
                                                        className="text-gold hover:text-white transition-colors flex items-center gap-2 mx-auto uppercase text-xs font-bold tracking-widest"
                                                    >
                                                        <X className="h-4 w-4" /> Remove Contract
                                                    </button>
                                                </motion.div>
                                            ) : (
                                                <motion.div
                                                    key="no-file"
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    className="space-y-4"
                                                >
                                                    <div className="h-20 w-20 rounded-2xl bg-white/5 flex items-center justify-center mx-auto border border-white/10 group-hover:border-gold/30 transition-colors">
                                                        <Upload className="h-10 w-10 text-slate-500 group-hover:text-gold transition-colors" />
                                                    </div>
                                                    <div>
                                                        <p className="text-lg font-bold text-white">Ingest Your Contract</p>
                                                        <p className="text-slate-500">Drag & drop or Click to browse (PDF, DOCX)</p>
                                                    </div>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Right Column: Features and Analysis */}
                    <div className="lg:col-span-5 space-y-8">
                        {/* Status / Feature Card */}
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.3 }}
                        >
                            <Card className="liquid-glass p-8 border-white/5">
                                <div className="space-y-8">
                                    <div className="flex items-center gap-3">
                                        <Zap className="h-5 w-5 text-amber" />
                                        <h3 className="text-lg font-bold text-white uppercase tracking-wider">Engine Process</h3>
                                    </div>

                                    {[
                                        { icon: Cpu, label: 'Deterministic Core', desc: 'No LLM hallucination for extraction', color: 'text-blue-400' },
                                        { icon: Sparkles, label: 'Statistical Broadening', desc: '4-step market cohort leveling', color: 'text-gold' },
                                        { icon: Shield, label: 'Red-Flag Shield', desc: '14+ critical risk assessments', color: 'text-red-400' },
                                    ].map((feature, idx) => (
                                        <div key={idx} className="flex gap-4">
                                            <div className={cn("mt-1 p-2 rounded-lg bg-white/5", feature.color)}>
                                                <feature.icon className="h-5 w-5" />
                                            </div>
                                            <div>
                                                <p className="font-bold text-white">{feature.label}</p>
                                                <p className="text-sm text-slate-500">{feature.desc}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </Card>
                        </motion.div>

                        {/* Analyze Button */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 0.4 }}
                        >
                            <button
                                className={cn(
                                    "w-full btn-primary h-20 text-xl font-black uppercase tracking-widest flex items-center justify-center gap-3",
                                    (!file || analyzeMutation.isPending || !context.role) && "opacity-20 cursor-not-allowed scale-100 grayscale"
                                )}
                                onClick={handleAnalyze}
                                disabled={!file || analyzeMutation.isPending || !context.role}
                            >
                                {analyzeMutation.isPending ? (
                                    <>
                                        <Loader2 className="h-8 w-8 animate-spin" />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        Run Analysis
                                        <ArrowRight className="h-8 w-8" />
                                    </>
                                )}
                            </button>
                        </motion.div>

                        {/* Error Message */}
                        <AnimatePresence>
                            {analyzeMutation.isError && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0 }}
                                    className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 flex gap-3 text-sm font-sans"
                                >
                                    <X className="h-5 w-5 shrink-0" />
                                    <div>
                                        <p className="font-bold uppercase tracking-wider mb-1">Engine Error</p>
                                        <p>{(analyzeMutation.error as any)?.message || "Internal Analysis Failure"}</p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    );
};
