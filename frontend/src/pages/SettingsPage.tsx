import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Settings, Server, ShieldCheck, Info } from 'lucide-react';

export const SettingsPage = () => {
    return (
        <div className="space-y-8 pb-20 max-w-4xl mx-auto">
            <div>
                <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Settings</h1>
                <p className="text-slate-500 mt-2">Application configuration and system status monitoring.</p>
            </div>

            <div className="grid gap-6">
                <Card className="shadow-premium border-none ring-1 ring-slate-200">
                    <CardHeader className="border-b bg-slate-50/50">
                        <CardTitle className="flex items-center space-x-2 text-sm">
                            <Server className="h-4 w-4 text-brand-500" />
                            <span>Backend Configuration</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-slate-900">API Elevation</p>
                                <p className="text-xs text-slate-500">Base URL for all analysis and KB requests.</p>
                            </div>
                            <code className="text-[10px] bg-slate-100 px-2 py-1 rounded font-mono text-slate-600">
                                {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
                            </code>
                        </div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-slate-900">Cache Strategy</p>
                                <p className="text-xs text-slate-500">File-based SHA256 persistence (Server-side).</p>
                            </div>
                            <Badge variant="info">DETERMINISTIC</Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card className="shadow-premium border-none ring-1 ring-slate-200">
                    <CardHeader className="border-b bg-slate-50/50">
                        <CardTitle className="flex items-center space-x-2 text-sm">
                            <ShieldCheck className="h-4 w-4 text-brand-500" />
                            <span>Security & Audit</span>
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-6 space-y-4">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-slate-900">LLM Mode</p>
                                <p className="text-xs text-slate-500">Sniper-first extraction fallback for non-sensitive data.</p>
                            </div>
                            <Badge variant="success">HYBRID</Badge>
                        </div>
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm font-bold text-slate-900">Data Privacy</p>
                                <p className="text-xs text-slate-500">Local embeddings via sentence-transformers.</p>
                            </div>
                            <Badge variant="secondary">LOCAL-FIRST</Badge>
                        </div>
                    </CardContent>
                </Card>

                <div className="rounded-xl border border-blue-100 bg-blue-50 p-6 flex flex-col items-center text-center space-y-3">
                    <Info className="h-6 w-6 text-brand-500" />
                    <div>
                        <h4 className="font-bold text-slate-900">About FairDeal v1.0.0</h4>
                        <p className="text-xs text-slate-600 mt-1 max-w-sm">
                            Built as a Principal-grade contract audit system.
                            Zero-placeholder implementation focused on auditability and market fairness.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};
