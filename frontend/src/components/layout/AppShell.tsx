import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';

export const AppShell = () => {
    return (
        <div className="flex min-h-screen bg-[#050505] text-slate-100">
            <Sidebar />
            <div className="flex flex-1 flex-col pl-64">
                <TopNav />
                <main className="flex-1">
                    <div className="mx-auto max-w-7xl">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
};
