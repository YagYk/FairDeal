import React from 'react';
import { motion } from 'framer-motion';

interface BellCurveProps {
    percentile: number;
    label: string;
}

export const BellCurve = ({ percentile, label }: BellCurveProps) => {
    // Generate points for a normal distribution curve
    const points = [];
    for (let i = 0; i <= 100; i++) {
        const x = i;
        // Standard normal distribution formula
        const y = Math.exp(-Math.pow(i - 50, 2) / (2 * Math.pow(15, 2))) * 100;
        points.push({ x, y });
    }

    const pathData = `M 0 100 ${points.map(p => `L ${p.x} ${100 - p.y}`).join(' ')} L 100 100 Z`;

    // Percentile marker position
    const markerX = percentile;

    return (
        <div className="relative w-full h-48 mt-8">
            <svg viewBox="0 0 100 105" className="w-full h-full overflow-visible">
                <defs>
                    <linearGradient id="curveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.2" />
                        <stop offset={`${percentile}%`} stopColor="#FFBF00" stopOpacity="0.6" />
                        <stop offset="100%" stopColor="#D4AF37" stopOpacity="0.1" />
                    </linearGradient>
                </defs>

                {/* The Curve */}
                <path
                    d={pathData}
                    fill="url(#curveGradient)"
                    stroke="rgba(212, 175, 55, 0.3)"
                    strokeWidth="0.5"
                />

                {/* Marker Line */}
                <motion.line
                    initial={{ y2: 100 }}
                    animate={{ y2: 0 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    x1={markerX}
                    y1="100"
                    x2={markerX}
                    y2="0"
                    stroke="#FFBF00"
                    strokeWidth="1"
                    strokeDasharray="2 1"
                />

                {/* Marker Label Bubble */}
                <motion.g
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1, duration: 0.5 }}
                >
                    <foreignObject x={markerX - 15} y="-25" width="30" height="20">
                        <div className="flex flex-col items-center">
                            <span className="text-[6px] font-black text-gold uppercase tracking-tighter bg-black/60 px-1 rounded-sm border border-gold/20">
                                You: {percentile}%
                            </span>
                            <div className="w-[1px] h-2 bg-gold/50" />
                        </div>
                    </foreignObject>
                </motion.g>

                {/* X-Axis labels */}
                <text x="0" y="110" fontSize="4" fill="rgba(255,255,255,0.3)" textAnchor="start">Lower 10%</text>
                <text x="50" y="110" fontSize="4" fill="rgba(255,255,255,0.3)" textAnchor="middle">Market Median</text>
                <text x="100" y="110" fontSize="4" fill="rgba(255,255,255,0.3)" textAnchor="end">Top 10%</text>
            </svg>
        </div>
    );
};
