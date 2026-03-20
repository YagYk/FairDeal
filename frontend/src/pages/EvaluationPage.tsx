import React, { useState } from 'react';
import {
  FlaskConical, Play, CheckCircle2, XCircle, BarChart3,
  TrendingUp, ArrowUpDown, Timer, Shield, Zap,
  ChevronDown, ChevronUp
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, CartesianGrid, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  Legend
} from 'recharts';
import { useRunEvaluation, useEvaluationResults } from '../lib/api';
import { EvaluationReport, ScoringTestResult } from '../lib/types';
import { cn } from '../lib/utils';

const GRADE_COLORS: Record<string, string> = {
  EXCEPTIONAL: '#22c55e',
  EXCELLENT: '#10b981',
  GOOD: '#3b82f6',
  FAIR: '#f59e0b',
  AVERAGE: '#f97316',
  'BELOW AVERAGE': '#ef4444',
  POOR: '#dc2626',
  CRITICAL: '#991b1b',
};

const CATEGORY_COLORS: Record<string, string> = {
  service: '#f97316',
  product: '#3b82f6',
  startup: '#a855f7',
  consulting: '#14b8a6',
};

function MetricCard({ label, value, sub, icon: Icon, accent = 'gold' }: {
  label: string; value: string | number; sub?: string;
  icon: React.ElementType; accent?: string;
}) {
  const accentClass = accent === 'green' ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
    : accent === 'blue' ? 'text-blue-400 bg-blue-400/10 border-blue-400/20'
    : accent === 'red' ? 'text-red-400 bg-red-400/10 border-red-400/20'
    : 'text-gold bg-gold/10 border-gold/20';

  return (
    <div className="rounded-2xl bg-white/5 border border-white/5 p-5 flex items-start gap-4">
      <div className={cn('h-10 w-10 rounded-xl flex items-center justify-center border', accentClass)}>
        <Icon className="h-5 w-5" />
      </div>
      <div>
        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">{label}</p>
        <p className="text-2xl font-serif font-bold text-white">{value}</p>
        {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}

function GradeBar({ grade, count, total }: { grade: string; count: number; total: number }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs font-bold text-slate-400 w-28 text-right truncate">{grade}</span>
      <div className="flex-1 h-6 bg-white/5 rounded-lg overflow-hidden">
        <div
          className="h-full rounded-lg transition-all duration-700"
          style={{ width: `${pct}%`, backgroundColor: GRADE_COLORS[grade] || '#666' }}
        />
      </div>
      <span className="text-xs font-bold text-white w-8">{count}</span>
    </div>
  );
}

function ResultRow({ r, idx }: { r: ScoringTestResult; idx: number }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <tr
        className={cn('border-b border-white/5 cursor-pointer hover:bg-white/[0.02] transition-colors', idx % 2 === 0 ? 'bg-transparent' : 'bg-white/[0.01]')}
        onClick={() => setOpen(!open)}
      >
        <td className="px-4 py-3 text-xs font-bold text-slate-500">{r.id}</td>
        <td className="px-4 py-3 text-sm font-bold text-white">{r.company}</td>
        <td className="px-4 py-3">
          <span className="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest"
            style={{ backgroundColor: (CATEGORY_COLORS[r.category] || '#666') + '20', color: CATEGORY_COLORS[r.category] || '#aaa' }}>
            {r.category}
          </span>
        </td>
        <td className="px-4 py-3 text-sm text-slate-400">{r.expected_range[0]}–{r.expected_range[1]}</td>
        <td className="px-4 py-3 text-sm font-bold text-white">{r.actual_score}</td>
        <td className="px-4 py-3">
          <span className="text-xs font-bold" style={{ color: GRADE_COLORS[r.grade] || '#aaa' }}>{r.grade}</span>
        </td>
        <td className="px-4 py-3 text-center">
          {r.passed
            ? <CheckCircle2 className="h-4 w-4 text-emerald-400 inline" />
            : <XCircle className="h-4 w-4 text-red-400 inline" />}
        </td>
        <td className="px-4 py-3 text-center text-slate-500">
          {open ? <ChevronUp className="h-4 w-4 inline" /> : <ChevronDown className="h-4 w-4 inline" />}
        </td>
      </tr>
      {open && (
        <tr className="bg-white/[0.02]">
          <td colSpan={8} className="px-6 py-4">
            <div className="grid grid-cols-5 gap-3 text-xs mb-3">
              {Object.entries(r.breakdown).map(([k, v]) => (
                <div key={k} className="rounded-xl bg-white/5 p-3 border border-white/5">
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{k}</p>
                  <p className="text-lg font-bold text-white">{v.score.toFixed(0)}</p>
                  <p className="text-slate-500">w: {(v.weight * 100).toFixed(0)}%</p>
                </div>
              ))}
            </div>
            {r.badges.length > 0 && (
              <div className="flex gap-2 mb-2">
                {r.badges.map((b, i) => (
                  <span key={i} className="px-2 py-0.5 bg-gold/10 text-gold rounded text-[10px] font-bold">{b}</span>
                ))}
              </div>
            )}
            {r.risk_factors.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {r.risk_factors.map((rf, i) => (
                  <span key={i} className="px-2 py-0.5 bg-red-500/10 text-red-400 rounded text-[10px] font-bold">{rf}</span>
                ))}
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

export const EvaluationPage: React.FC = () => {
  const { data: cached, isLoading: loadingCached } = useEvaluationResults();
  const runMutation = useRunEvaluation();

  const report: EvaluationReport | undefined = runMutation.data || cached;
  const loading = loadingCached || runMutation.isPending;

  const handleRun = () => runMutation.mutate();

  if (loading && !report) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center space-y-4">
          <div className="h-12 w-12 rounded-2xl bg-gold/10 border border-gold/20 flex items-center justify-center mx-auto animate-pulse">
            <FlaskConical className="h-6 w-6 text-gold" />
          </div>
          <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Running evaluation suite…</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-center space-y-6">
          <div className="h-16 w-16 rounded-2xl bg-gold/10 border border-gold/20 flex items-center justify-center mx-auto">
            <FlaskConical className="h-8 w-8 text-gold" />
          </div>
          <div>
            <h2 className="text-2xl font-serif font-bold text-white mb-2">Validation Metrics</h2>
            <p className="text-sm text-slate-500 max-w-md">
              Run the full validation suite to generate IEEE-paper-ready metrics for the scoring engine.
            </p>
          </div>
          <button onClick={handleRun} className="btn-primary px-8 py-3 flex items-center gap-2 mx-auto">
            <Play className="h-4 w-4" /> Run Evaluation
          </button>
        </div>
      </div>
    );
  }

  const scatterData = report.scoring_results.map(r => ({
    name: r.company,
    ctc: r.ctc_inr / 100000,
    score: r.actual_score,
    category: r.category,
  }));

  const gradeChartData = Object.entries(report.grade_distribution)
    .filter(([, v]) => v > 0)
    .map(([grade, count]) => ({ grade, count, fill: GRADE_COLORS[grade] || '#666' }));

  const categoryChartData = Object.entries(report.category_means).map(([cat, mean]) => ({
    category: cat.charAt(0).toUpperCase() + cat.slice(1),
    mean: Math.round(mean * 100) / 100,
    fill: CATEGORY_COLORS[cat] || '#666',
  }));

  const componentData = Object.entries(report.component_stats).map(([comp, stats]) => ({
    component: comp.charAt(0).toUpperCase() + comp.slice(1),
    mean: stats.mean,
    fullMark: 100,
  }));

  const correlationData = report.feature_correlations.map(c => ({
    feature: c.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    r: Math.round(c.pearson_r * 1000) / 1000,
    fill: c.pearson_r > 0 ? '#3b82f6' : '#ef4444',
    abs: Math.abs(c.pearson_r),
  }));

  return (
    <div className="space-y-8 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif font-bold text-white tracking-tight">Validation Metrics</h1>
          <p className="text-sm text-slate-500 mt-1">
            Engine v{report.engine_version} · {report.total_test_cases} test cases · {report.evaluation_time_ms.toFixed(0)}ms
          </p>
        </div>
        <button onClick={handleRun} disabled={runMutation.isPending}
          className="btn-primary px-5 py-2.5 flex items-center gap-2 text-sm">
          <Play className="h-4 w-4" />
          {runMutation.isPending ? 'Running…' : 'Re-run'}
        </button>
      </div>

      {/* ═══ Top Metrics ═══ */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={CheckCircle2} label="Pass Rate" value={`${report.scoring_pass_rate}%`}
          sub={`${report.scoring_results.filter(r => r.passed).length}/${report.total_test_cases} passed`} accent="green" />
        <MetricCard icon={ArrowUpDown} label="Ordering Accuracy" value={`${report.known_ordering_accuracy}%`}
          sub={`${report.known_ordering_correct}/${report.known_ordering_total} pairs`} accent="blue" />
        <MetricCard icon={Shield} label="Determinism" value={`${report.determinism_score}%`}
          sub={`${report.determinism_runs} identical runs`} accent="green" />
        <MetricCard icon={Timer} label="Eval Time" value={`${report.evaluation_time_ms.toFixed(0)}ms`}
          sub={`${(report.evaluation_time_ms / report.total_test_cases).toFixed(1)}ms/case`} />
      </div>

      {/* ═══ Score Distribution ═══ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution Stats */}
        <div className="rounded-2xl bg-white/5 border border-white/5 p-6">
          <div className="flex items-center gap-2 mb-5">
            <BarChart3 className="h-5 w-5 text-gold" />
            <h3 className="text-lg font-bold text-white uppercase tracking-widest">Score Distribution</h3>
          </div>
          <div className="grid grid-cols-3 gap-4 mb-5">
            {[
              ['Mean', report.score_distribution.mean],
              ['Median', report.score_distribution.median],
              ['Std Dev', report.score_distribution.std_dev],
              ['Min', report.score_distribution.min_score],
              ['Max', report.score_distribution.max_score],
              ['IQR', report.score_distribution.iqr],
            ].map(([label, val]) => (
              <div key={label as string} className="text-center p-3 rounded-xl bg-white/5">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{label as string}</p>
                <p className="text-xl font-bold text-white mt-1">{(val as number).toFixed(1)}</p>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-white/5 text-center">
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Skewness</p>
              <p className="text-lg font-bold text-white mt-1">{report.score_distribution.skewness.toFixed(3)}</p>
              <p className="text-[10px] text-slate-500">
                {Math.abs(report.score_distribution.skewness) < 0.5 ? 'Approx. symmetric' : report.score_distribution.skewness > 0 ? 'Right-skewed' : 'Left-skewed'}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-white/5 text-center">
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Kurtosis</p>
              <p className="text-lg font-bold text-white mt-1">{report.score_distribution.kurtosis.toFixed(3)}</p>
              <p className="text-[10px] text-slate-500">
                {Math.abs(report.score_distribution.kurtosis) < 1 ? 'Mesokurtic (normal-like)' : report.score_distribution.kurtosis > 0 ? 'Leptokurtic' : 'Platykurtic'}
              </p>
            </div>
          </div>
        </div>

        {/* Grade Distribution Chart */}
        <div className="rounded-2xl bg-white/5 border border-white/5 p-6">
          <div className="flex items-center gap-2 mb-5">
            <BarChart3 className="h-5 w-5 text-gold" />
            <h3 className="text-lg font-bold text-white uppercase tracking-widest">Grade Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={gradeChartData} layout="vertical" margin={{ left: 10 }}>
              <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis dataKey="grade" type="category" tick={{ fill: '#94a3b8', fontSize: 11 }} width={100} />
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: 12, fontSize: 12 }} />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {gradeChartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ═══ Category Comparison & Correlations ═══ */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Means */}
        <div className="rounded-2xl bg-white/5 border border-white/5 p-6">
          <div className="flex items-center gap-2 mb-5">
            <TrendingUp className="h-5 w-5 text-gold" />
            <h3 className="text-lg font-bold text-white uppercase tracking-widest">Category Means</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={categoryChartData} margin={{ bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="category" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: 12, fontSize: 12 }} />
              <Bar dataKey="mean" radius={[6, 6, 0, 0]}>
                {categoryChartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          {report.category_comparisons.length > 0 && (
            <div className="mt-4 space-y-2">
              {report.category_comparisons.map((c, i) => (
                <div key={i} className="flex items-center justify-between text-xs p-2 rounded-lg bg-white/[0.02]">
                  <span className="text-slate-400">
                    {c.category_a} vs {c.category_b}
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-slate-500">t={c.t_statistic.toFixed(2)}</span>
                    <span className={cn('px-1.5 py-0.5 rounded font-bold', c.significant ? 'bg-emerald-500/10 text-emerald-400' : 'bg-white/5 text-slate-500')}>
                      {c.significant ? `p<0.05 (d=${c.effect_size.toFixed(2)})` : 'n.s.'}
                    </span>
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Feature Correlations */}
        <div className="rounded-2xl bg-white/5 border border-white/5 p-6">
          <div className="flex items-center gap-2 mb-5">
            <Zap className="h-5 w-5 text-gold" />
            <h3 className="text-lg font-bold text-white uppercase tracking-widest">Feature Correlations</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={correlationData} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" domain={[-1, 1]} tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis dataKey="feature" type="category" tick={{ fill: '#94a3b8', fontSize: 10 }} width={120} />
              <Tooltip contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: 12, fontSize: 12 }}
                formatter={(val: number | undefined) => [`r = ${(val ?? 0).toFixed(4)}`, 'Pearson r']} />
              <Bar dataKey="r" radius={4}>
                {correlationData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-1.5">
            {report.feature_correlations.map((c, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="text-slate-400">{c.feature.replace(/_/g, ' ')}</span>
                <span className={cn('font-bold',
                  c.strength === 'strong' ? 'text-emerald-400' : c.strength === 'moderate' ? 'text-blue-400' : 'text-slate-500')}>
                  r={c.pearson_r.toFixed(4)} ({c.strength} {c.direction})
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ═══ Scatter: CTC vs Score ═══ */}
      <div className="rounded-2xl bg-white/5 border border-white/5 p-6">
        <div className="flex items-center gap-2 mb-5">
          <TrendingUp className="h-5 w-5 text-gold" />
          <h3 className="text-lg font-bold text-white uppercase tracking-widest">CTC vs Fairness Score</h3>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <ScatterChart margin={{ bottom: 20, left: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="ctc" name="CTC (₹L)" unit="L" tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: 'CTC (₹ Lakhs)', position: 'insideBottomRight', offset: -5, fill: '#64748b', fontSize: 11 }} />
            <YAxis dataKey="score" name="Score" domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }}
              label={{ value: 'Fairness Score', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
            <Tooltip contentStyle={{ background: '#111', border: '1px solid #333', borderRadius: 12, fontSize: 12 }}
              formatter={(val: number | undefined, name: string | undefined) => [name === 'CTC (₹L)' ? `₹${val ?? 0}L` : (val ?? 0), name ?? '']} />
            <Legend />
            {Object.entries(CATEGORY_COLORS).map(([cat, color]) => {
              const d = scatterData.filter(s => s.category === cat);
              return d.length > 0 ? (
                <Scatter key={cat} name={cat.charAt(0).toUpperCase() + cat.slice(1)} data={d} fill={color} />
              ) : null;
            })}
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* ═══ Component Radar ═══ */}
      <div className="rounded-2xl bg-white/5 border border-white/5 p-6">
        <div className="flex items-center gap-2 mb-5">
          <Shield className="h-5 w-5 text-gold" />
          <h3 className="text-lg font-bold text-white uppercase tracking-widest">Component Score Means</h3>
        </div>
        <div className="flex items-center justify-center">
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={componentData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="#1e293b" />
              <PolarAngleAxis dataKey="component" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
              <Radar name="Mean Score" dataKey="mean" stroke="#d4af37" fill="#d4af37" fillOpacity={0.25} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="grid grid-cols-5 gap-3 mt-4">
          {Object.entries(report.component_stats).map(([comp, stats]) => (
            <div key={comp} className="text-center p-3 rounded-xl bg-white/5 border border-white/5">
              <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{comp}</p>
              <p className="text-lg font-bold text-white mt-1">{stats.mean.toFixed(1)}</p>
              <p className="text-[10px] text-slate-500">σ={stats.std.toFixed(1)}</p>
              <p className="text-[10px] text-slate-500">[{stats.min.toFixed(0)}–{stats.max.toFixed(0)}]</p>
            </div>
          ))}
        </div>
      </div>

      {/* ═══ Per-Contract Results Table ═══ */}
      <div className="rounded-2xl bg-white/5 border border-white/5 overflow-hidden">
        <div className="p-6 border-b border-white/5">
          <div className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-gold" />
            <h3 className="text-lg font-bold text-white uppercase tracking-widest">Per-Contract Results</h3>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/10">
                {['ID', 'Company', 'Category', 'Expected', 'Actual', 'Grade', 'Pass', ''].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {report.scoring_results.map((r, i) => <ResultRow key={r.id} r={r} idx={i} />)}
            </tbody>
          </table>
        </div>
      </div>

      {/* ═══ IEEE Summary Table ═══ */}
      <div className="rounded-2xl bg-white/5 border border-white/5 p-6">
        <div className="flex items-center gap-2 mb-5">
          <BarChart3 className="h-5 w-5 text-gold" />
          <h3 className="text-lg font-bold text-white uppercase tracking-widest">IEEE Paper Summary</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-4 py-2 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Metric</th>
                <th className="px-4 py-2 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Value</th>
                <th className="px-4 py-2 text-left text-[10px] font-black text-slate-500 uppercase tracking-widest">Interpretation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              <tr>
                <td className="px-4 py-2.5 text-slate-400">Scoring Validation Pass Rate</td>
                <td className="px-4 py-2.5 font-bold text-emerald-400">{report.scoring_pass_rate}%</td>
                <td className="px-4 py-2.5 text-slate-500">Scores fall within expected ranges</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 text-slate-400">Known Ordering Compliance</td>
                <td className="px-4 py-2.5 font-bold text-blue-400">{report.known_ordering_accuracy}%</td>
                <td className="px-4 py-2.5 text-slate-500">Contract pairs correctly ranked</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 text-slate-400">Determinism</td>
                <td className="px-4 py-2.5 font-bold text-emerald-400">{report.determinism_score}%</td>
                <td className="px-4 py-2.5 text-slate-500">Identical outputs across {report.determinism_runs} runs</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 text-slate-400">Score Mean ± SD</td>
                <td className="px-4 py-2.5 font-bold text-white">{report.score_distribution.mean} ± {report.score_distribution.std_dev}</td>
                <td className="px-4 py-2.5 text-slate-500">Healthy spread across score range</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 text-slate-400">Score Range</td>
                <td className="px-4 py-2.5 font-bold text-white">{report.score_distribution.min_score}–{report.score_distribution.max_score}</td>
                <td className="px-4 py-2.5 text-slate-500">Full utilization of scoring range</td>
              </tr>
              <tr>
                <td className="px-4 py-2.5 text-slate-400">Skewness</td>
                <td className="px-4 py-2.5 font-bold text-white">{report.score_distribution.skewness.toFixed(3)}</td>
                <td className="px-4 py-2.5 text-slate-500">{Math.abs(report.score_distribution.skewness) < 0.5 ? 'Approximately symmetric distribution' : 'Slight asymmetry'}</td>
              </tr>
              {report.feature_correlations.map(c => (
                <tr key={c.feature}>
                  <td className="px-4 py-2.5 text-slate-400">r({c.feature.replace(/_/g, ' ')})</td>
                  <td className="px-4 py-2.5 font-bold" style={{ color: c.pearson_r > 0 ? '#3b82f6' : '#ef4444' }}>{c.pearson_r.toFixed(4)}</td>
                  <td className="px-4 py-2.5 text-slate-500">{c.strength} {c.direction} correlation</td>
                </tr>
              ))}
              {report.category_comparisons.map((c, i) => (
                <tr key={i}>
                  <td className="px-4 py-2.5 text-slate-400">{c.category_a} vs {c.category_b}</td>
                  <td className="px-4 py-2.5 font-bold text-white">t={c.t_statistic.toFixed(2)}, d={c.effect_size.toFixed(2)}</td>
                  <td className="px-4 py-2.5 text-slate-500">{c.significant ? 'Statistically significant difference' : 'No significant difference'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
