import { Bell, User, Search, Settings, Shield } from 'lucide-react';
import { Button } from '../ui/Button';

export const TopNav = () => {
    return (
        <header className="fixed inset-x-0 top-0 z-30 h-16 border-b border-white/5 bg-slate-950/50 backdrop-blur-xl">
            <div className="flex h-full items-center justify-between px-6">
                <div className="flex items-center space-x-4 ml-64">
                    {/* ml-64 to compensate for sidebar */}
                    <div className="relative w-96 group">
                        <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500 group-focus-within:text-gold transition-colors" />
                        <input
                            type="text"
                            placeholder="Universal search..."
                            className="h-10 w-full rounded-2xl border border-white/5 bg-white/5 pl-11 pr-4 text-sm text-white focus:border-gold/30 focus:outline-none focus:ring-1 focus:ring-gold/30 transition-all placeholder:text-slate-600"
                        />
                    </div>
                </div>

                <div className="flex items-center space-x-6">
                    <div className="flex items-center gap-1 group cursor-pointer">
                        <div className="h-8 w-8 rounded-xl bg-gold/10 flex items-center justify-center border border-gold/20">
                            <Shield className="h-4 w-4 text-gold" />
                        </div>
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gold opacity-0 group-hover:opacity-100 transition-opacity">PRO</span>
                    </div>

                    <Button variant="ghost" size="icon" className="relative text-slate-400 hover:text-white hover:bg-white/5 rounded-xl">
                        <Bell className="h-5 w-5" />
                        <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-gold shadow-[0_0_8px_rgba(212,175,55,0.8)]" />
                    </Button>

                    <div className="h-8 w-px bg-white/5" />

                    <div className="flex items-center space-x-3 pl-2 group cursor-pointer">
                        <div className="flex flex-col text-right">
                            <span className="text-xs font-bold text-white tracking-tight">Alex Rivera</span>
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Premium Plan</span>
                        </div>
                        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/5 text-gold font-serif italic font-bold border border-white/10 group-hover:border-gold/50 transition-all">
                            AR
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
};
