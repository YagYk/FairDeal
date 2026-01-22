import React, { useEffect, useState } from 'react';
import { CompanyType, Context } from '../../lib/types';
import { User, Briefcase, Building2, MapPin, Globe } from 'lucide-react';
import { cn } from '../../lib/utils';
import { motion } from 'framer-motion';

interface ContextFormProps {
    onContextChange: (context: Context) => void;
    initialContext?: Context;
}

export const ContextForm = ({ onContextChange, initialContext }: ContextFormProps) => {
    const [role, setRole] = useState(initialContext?.role || '');
    const [experience, setExperience] = useState(initialContext?.experience_level?.toString() || '1');
    const [companyType, setCompanyType] = useState<CompanyType>(initialContext?.company_type || CompanyType.PRODUCT);
    const [location, setLocation] = useState(initialContext?.location || 'mumbai');
    const [industry, setIndustry] = useState(initialContext?.industry || 'tech');

    useEffect(() => {
        const ctx: Context = {
            role,
            experience_level: parseFloat(experience),
            company_type: companyType,
            location,
            industry
        };
        onContextChange(ctx);
    }, [role, experience, companyType, location, industry, onContextChange]);

    return (
        <div className="space-y-8 font-sans">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <User className="w-3.5 h-3.5" />
                        Target Role
                    </label>
                    <input
                        type="text"
                        placeholder="e.g. Senior Software Engineer"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white focus:border-gold/50 focus:ring-1 focus:ring-gold/50 transition-all outline-none placeholder:text-slate-600"
                    />
                </div>

                <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Briefcase className="w-3.5 h-3.5" />
                        Experience Level
                    </label>
                    <div className="relative">
                        <select
                            value={experience}
                            onChange={(e) => setExperience(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white focus:border-gold/50 focus:ring-1 focus:ring-gold/50 transition-all outline-none appearance-none"
                        >
                            <option value="1" className="bg-[#121212]">0-2 years (Entry)</option>
                            <option value="4" className="bg-[#121212]">2-5 years (Mid)</option>
                            <option value="8" className="bg-[#121212]">5-10 years (Senior)</option>
                            <option value="15" className="bg-[#121212]">10+ years (Lead/Staff)</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <MapPin className="w-3.5 h-3.5" />
                        Location
                    </label>
                    <input
                        type="text"
                        placeholder="e.g. Mumbai, Bengaluru, Remote"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white focus:border-gold/50 focus:ring-1 focus:ring-gold/50 transition-all outline-none placeholder:text-slate-600"
                    />
                </div>

                <div>
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Globe className="w-3.5 h-3.5" />
                        Industry
                    </label>
                    <select
                        value={industry}
                        onChange={(e) => setIndustry(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5 text-white focus:border-gold/50 focus:ring-1 focus:ring-gold/50 transition-all outline-none appearance-none"
                    >
                        <option value="tech" className="bg-[#121212]">Technology / SaaS</option>
                        <option value="finance" className="bg-[#121212]">Finance / Fintech</option>
                        <option value="health" className="bg-[#121212]">Healthcare</option>
                        <option value="manufacturing" className="bg-[#121212]">Manufacturing</option>
                    </select>
                </div>
            </div>

            <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <Building2 className="w-3.5 h-3.5" />
                    Company Archetype
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {[
                        { id: CompanyType.PRODUCT, label: 'Product', desc: 'Big Tech, SaaS' },
                        { id: CompanyType.SERVICE, label: 'Service', desc: 'Consulting, Agencies' },
                        { id: CompanyType.STARTUP, label: 'Early Startup', desc: 'Equity Heavy' },
                    ].map((type) => (
                        <button
                            key={type.id}
                            onClick={() => setCompanyType(type.id)}
                            className={cn(
                                "flex flex-col items-start rounded-2xl border p-4 text-left transition-all duration-300",
                                companyType === type.id
                                    ? 'border-gold bg-gold/5 ring-1 ring-gold/20'
                                    : 'border-white/5 bg-white/5 hover:border-gold/30 hover:bg-white/10'
                            )}
                        >
                            <span className={cn(
                                "text-sm font-bold tracking-tight",
                                companyType === type.id ? 'text-gold' : 'text-slate-300'
                            )}>
                                {type.label}
                            </span>
                            <span className="text-[10px] text-slate-500 uppercase tracking-widest mt-1 font-bold">{type.desc}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};
