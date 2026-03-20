import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Ghost } from 'lucide-react';

export const NotFound = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
            <div className="h-24 w-24 bg-white/5 rounded-full flex items-center justify-center border border-white/10 animate-bounce">
                <Ghost className="h-12 w-12 text-slate-500" />
            </div>
            <div>
                <h2 className="text-3xl font-black text-white tracking-tighter">404 - LOST IN THE KB</h2>
                <p className="text-slate-500 mt-2">The clause or page you are looking for has drifted into non-existence.</p>
            </div>
            <Link to="/">
                <button className="btn-primary px-8 py-3 rounded-full font-bold">Return Home</button>
            </Link>
        </div>
    );
};
