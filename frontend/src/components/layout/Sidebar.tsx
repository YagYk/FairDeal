import { NavLink } from 'react-router-dom';
import {
    BarChart3,
    Database,
    Search,
    Settings,
    ShieldCheck,
    LayoutDashboard
} from 'lucide-react';
import { cn } from '../../lib/utils';

const navItems = [
    { name: 'Analyze', icon: LayoutDashboard, href: '/' },
    { name: 'Knowledge Base', icon: Database, href: '/kb' },
    { name: 'Search', icon: Search, href: '/kb/search' },
    { name: 'Settings', icon: Settings, href: '/settings' },
];

export const Sidebar = () => {
    return (
        <aside className="fixed inset-y-0 left-0 z-40 w-64 border-r border-white/5 bg-[#050505] text-slate-400">
            <div className="flex h-16 items-center px-6 border-b border-white/5">
                <div className="flex items-center space-x-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gold/10 text-gold border border-gold/20 shadow-[0_0_15px_rgba(212,175,55,0.1)]">
                        <ShieldCheck className="h-5 w-5" />
                    </div>
                    <span className="text-xl font-serif font-bold tracking-tight text-white italic">FairDeal</span>
                </div>
            </div>

            <nav className="flex-1 space-y-1 px-4 py-8">
                {navItems.map((item) => (
                    <NavLink
                        key={item.href}
                        to={item.href}
                        className={({ isActive }) =>
                            cn(
                                'group flex items-center rounded-2xl px-4 py-3 text-sm font-bold tracking-tight transition-all duration-300',
                                isActive
                                    ? 'bg-gold/10 text-gold shadow-[inset_0_0_0_1px_rgba(212,175,55,0.2)]'
                                    : 'text-slate-500 hover:bg-white/5 hover:text-white'
                            )
                        }
                    >
                        {({ isActive }) => (
                            <>
                                <item.icon
                                    className={cn(
                                        'mr-3 h-5 w-5 transition-transform duration-300 group-hover:scale-110',
                                        isActive ? 'text-gold' : 'text-slate-600 group-hover:text-slate-300'
                                    )}
                                />
                                {item.name}
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            <div className="border-t border-white/5 p-6">
                <div className="rounded-3xl bg-white/5 p-5 border border-white/10 relative overflow-hidden group">
                    <div className="absolute inset-0 bg-gold/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 relative z-10">Engine Status</p>
                    <div className="flex items-center space-x-2 relative z-10">
                        <div className="h-2 w-2 rounded-full bg-gold shadow-[0_0_10px_rgba(212,175,55,0.8)] animate-pulse" />
                        <span className="text-xs font-bold text-slate-300 tracking-tight">Active & Ready</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};
