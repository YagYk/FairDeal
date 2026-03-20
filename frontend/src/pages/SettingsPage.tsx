import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Settings, Server, ShieldCheck, Info } from 'lucide-react';

export const SettingsPage = () => {
    return (
        <div className="space-y-8 pb-20 max-w-4xl mx-auto">
            <div>
                <h1 className="text-3xl font-serif font-bold text-white tracking-tight">Settings</h1>
                <p className="text-slate-400 mt-2">Application configuration and system status monitoring.</p>
            </div>

            <div className="grid gap-6">
                <Card className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden">
                    <CardHeader className="border-b border-white/5 bg-white/5">
                        <CardTitle className="flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                            <Server className="h-4 w-4 text-gold" />
                            <span>Backend Configuration</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-white">API Endpoint</p>
                                <p className="text-xs text-slate-500">Base URL for all analysis and KB requests.</p>
                            </div>
                            <code className="text-[10px] bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg font-mono text-gold/80">
                                {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
                            </code>
                        </div>
                        <div className="h-px bg-white/5" />
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-white">Cache Strategy</p>
                                <p className="text-xs text-slate-500">File-based SHA256 persistence (Server-side).</p>
                            </div>
                            <Badge variant="info">DETERMINISTIC</Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-white/5 bg-white/5 backdrop-blur-xl overflow-hidden">
                    <CardHeader className="border-b border-white/5 bg-white/5">
                        <CardTitle className="flex items-center space-x-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
                            <ShieldCheck className="h-4 w-4 text-gold" />
                            <span>Security & Audit</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-white">LLM Mode</p>
                                <p className="text-xs text-slate-500">Sniper-first extraction fallback for non-sensitive data.</p>
                            </div>
                            <Badge variant="success">HYBRID</Badge>
                        </div>
                        <div className="h-px bg-white/5" />
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-white">Data Privacy</p>
                                <p className="text-xs text-slate-500">Local embeddings via sentence-transformers.</p>
                            </div>
                            <Badge variant="secondary">LOCAL-FIRST</Badge>
                        </div>
                    </CardContent>
                </Card>

                <div className="rounded-3xl border border-gold/10 bg-gold/5 p-8 flex flex-col items-center text-center space-y-3 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <Info className="h-6 w-6 text-gold relative z-10" />
                    <div className="relative z-10">
                        <h4 className="font-bold text-white">About FairDeal v1.0.0</h4>
                        <p className="text-xs text-slate-400 mt-1 max-w-sm">
                            Built as a Principal-grade contract audit system.
                            Zero-placeholder implementation focused on auditability and market fairness.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
