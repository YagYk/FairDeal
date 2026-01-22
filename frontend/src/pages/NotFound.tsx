import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Ghost } from 'lucide-react';

export const NotFound = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
            <div className="h-24 w-24 bg-slate-100 rounded-full flex items-center justify-center animate-bounce">
                <Ghost className="h-12 w-12 text-slate-400" />
            </div>
            <div>
                <h2 className="text-3xl font-black text-slate-900 tracking-tighter">404 - LOST IN THE KB</h2>
                <p className="text-slate-500 mt-2">The clause or page you are looking for has drifted into non-existence.</p>
            </div>
            <Link to="/">
                <Button variant="primary">Return Home</Button>
            </Link>
        </div>
    );
};
