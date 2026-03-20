import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload, FileText, TrendingUp, AlertTriangle, CheckCircle2,
  Target, Lightbulb, Download, Copy, Check, Sparkles,
  BarChart3, Percent, Users, Clock
} from 'lucide-react';
import { ContextForm } from '../components/analyze/ContextForm';
import { useAnalyzeContract } from '../lib/api';
import { Context, CompanyType, AnalyzeResponse } from '../lib/types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { cn } from '../lib/utils';

interface AnalysisProgress {
  stage: string;
  progress: number;
  message: string;
}

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [context, setContext] = useState<Context>(() => {
    const saved = localStorage.getItem('fairdeal_context');
    return saved ? JSON.parse(saved) : {
      role: '',
      experience_level: 1,
      company_type: CompanyType.PRODUCT
    };
  });
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [copiedScript, setCopiedScript] = useState<string | null>(null);

  const analyzeMutation = useAnalyzeContract();

  useEffect(() => {
    if (context) {
      localStorage.setItem('fairdeal_context', JSON.stringify(context));
    }
  }, [context]);

  const handleAnalyze = async () => {
    if (!file) return;

    const progressStages = [
      { stage: 'parse', progress: 20, message: 'Extracting text from contract...' },
      { stage: 'extract', progress: 40, message: 'Finding salary: ₹18,00,000' },
      { stage: 'extract', progress: 50, message: 'Finding notice: 30 days' },
      { stage: 'benchmark', progress: 70, message: 'Comparing with 42 similar contracts...' },
      { stage: 'score', progress: 90, message: 'Computing fairness score...' },
      { stage: 'complete', progress: 100, message: 'Analysis complete!' },
    ];

    for (const stage of progressStages) {
      setProgress(stage);
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    try {
      const data = await analyzeMutation.mutateAsync({ file, context });
      setResult(data);
      setProgress(null);
    } catch (error) {
      console.error('Analysis failed', error);
      setProgress(null);
    }
  };

  const copyScript = (script: string, id: string) => {
    navigator.clipboard.writeText(script);
    setCopiedScript(id);
    setTimeout(() => setCopiedScript(null), 2000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 60) return 'text-blue-400';
    if (score >= 40) return 'text-amber-400';
    if (score >= 20) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBorderColor = (score: number) => {
    if (score >= 80) return 'border-emerald-500/20';
    if (score >= 60) return 'border-blue-500/20';
    if (score >= 40) return 'border-amber-500/20';
    if (score >= 20) return 'border-orange-500/20';
    return 'border-red-500/20';
  };

  const getGradeEmoji = (grade: string) => {
    switch (grade) {
      case 'EXCELLENT': return '⭐';
      case 'GOOD': return '✨';
      case 'FAIR': return '📊';
      case 'POOR': return '⚠️';
      case 'CRITICAL': return '🚨';
      default: return '📄';
    }
  };

  return (
    <div className="space-y-8 pb-20">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-4xl font-serif font-bold text-white tracking-tight">
          FairDeal Contract Intelligence
        </h1>
        <p className="text-lg text-slate-400">
          From anxiety to clarity in 3 seconds. Know exactly what's unfair, why it matters, and how to negotiate.
        </p>
      </div>

      {/* Upload Section */}
      {!result && (
        <Card className="liquid-glass p-8 border-white/5">
          <div className="space-y-6">
            <ContextForm
              onContextChange={setContext}
              initialContext={context}
            />

            <div className="border-2 border-dashed border-white/10 rounded-2xl p-12 text-center hover:border-gold/30 transition-colors group">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".pdf,.docx"
                onChange={(e) => {
                  const selected = e.target.files?.[0];
                  if (selected) setFile(selected);
                }}
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center space-y-4"
              >
                <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:border-gold/30 transition-colors">
                  <Upload className="w-8 h-8 text-slate-500 group-hover:text-gold transition-colors" />
                </div>
                <div>
                  <p className="text-lg font-bold text-white">
                    {file ? file.name : 'Upload Your Contract'}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    PDF or DOCX files only
                  </p>
                </div>
              </label>
            </div>

            <button
              onClick={handleAnalyze}
              disabled={!file || analyzeMutation.isPending}
              className={cn(
                "w-full btn-primary h-14 text-lg font-black uppercase tracking-widest flex items-center justify-center gap-3",
                (!file || analyzeMutation.isPending) && "opacity-20 cursor-not-allowed scale-100 grayscale"
              )}
            >
              {analyzeMutation.isPending ? (
                <>
                  <Clock className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5" />
                  Analyze Contract
                </>
              )}
            </button>
          </div>
        </Card>
      )}

      {/* Progress Indicator */}
      {progress && !result && (
        <Card className="liquid-glass p-8 border-gold/10">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-white">
                {progress.message}
              </h3>
              <span className="text-sm font-bold text-gold">
                {progress.progress}%
              </span>
            </div>
            <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-gold to-amber h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress.progress}%` }}
              />
            </div>
            <div className="flex items-center flex-wrap gap-4 text-sm text-slate-500">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4 text-gold" />
                Extracted text ({Math.round(progress.progress * 0.3)}ms)
              </span>
              {progress.progress > 40 && (
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-gold" />
                  Found salary
                </span>
              )}
              {progress.progress > 50 && (
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-gold" />
                  Found notice period
                </span>
              )}
              {progress.progress > 70 && (
                <span className="flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4 text-gold" />
                  Comparing with similar contracts
                </span>
              )}
            </div>
          </div>
        </Card>
      )}

      {/* Results Dashboard */}
      {result && (
        <div className="space-y-8">
          {/* Score Card */}
          <Card className={cn("liquid-glass p-8 border-2", getScoreBorderColor(result.score))}>
            <div className="text-center space-y-6">
              <div className="flex items-center justify-center space-x-4">
                <span className="text-5xl">{getGradeEmoji(result.grade)}</span>
                <div>
                  <h2 className={cn("text-6xl font-serif font-bold", getScoreColor(result.score))}>
                    {Math.round(result.score)}/100
                  </h2>
                  <p className="text-lg font-bold text-slate-300 mt-1 uppercase tracking-widest">
                    {result.grade} CONTRACT
                  </p>
                </div>
              </div>

              <div className="w-full bg-white/5 rounded-full h-3 overflow-hidden max-w-md mx-auto">
                <div
                  className="bg-gradient-to-r from-gold to-amber h-full rounded-full transition-all duration-1000"
                  style={{ width: `${result.score}%` }}
                />
              </div>

              {result.contract_metadata.role_title && (
                <p className="text-sm text-slate-500">
                  {result.contract_metadata.company_name || 'Company'} • {result.contract_metadata.role_title}
                </p>
              )}
            </div>
          </Card>

          {/* How You Compare */}
          {Object.keys(result.percentiles).length > 0 && (
            <Card className="liquid-glass p-8 border-white/5">
              <div className="flex items-center space-x-3 mb-6">
                <BarChart3 className="w-5 h-5 text-gold" />
                <h3 className="text-xl font-bold text-white uppercase tracking-widest">How You Compare</h3>
              </div>

              <div className="space-y-6">
                {result.percentiles.salary && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-white">
                        Salary ({result.percentiles.salary.field_display})
                      </span>
                      <span className="text-sm font-bold text-gold">
                        {result.percentiles.salary.value.toFixed(1)}th percentile
                      </span>
                    </div>
                    <div className="w-full bg-white/5 rounded-full h-5 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-gold to-amber h-full rounded-full flex items-center justify-end pr-2"
                        style={{ width: `${result.percentiles.salary.value}%` }}
                      >
                        <span className="text-[10px] font-bold text-charcoal">
                          Better than {result.percentiles.salary.value.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-400 mt-2">
                      {result.percentiles.salary.insight}
                    </p>
                  </div>
                )}

                {result.percentiles.notice_period && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-white">
                        Notice Period ({result.percentiles.notice_period.field_display})
                      </span>
                      <span className="text-sm font-bold text-emerald-400">
                        {result.percentiles.notice_period.value.toFixed(1)}th percentile
                        {result.percentiles.notice_period.interpretation === 'excellent' && (
                          <span className="ml-2">⭐ EXCELLENT</span>
                        )}
                      </span>
                    </div>
                    <div className="w-full bg-white/5 rounded-full h-5 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-emerald-500 to-emerald-400 h-full rounded-full flex items-center justify-end pr-2"
                        style={{ width: `${100 - result.percentiles.notice_period.value}%` }}
                      >
                        <span className="text-[10px] font-bold text-charcoal">
                          Shorter than {100 - Math.round(result.percentiles.notice_period.value)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-400 mt-2">
                      {result.percentiles.notice_period.insight}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Red Flags */}
          {result.red_flags.length > 0 && (
            <Card className="liquid-glass p-8 border-red-500/20">
              <div className="flex items-center space-x-3 mb-6">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <h3 className="text-xl font-bold text-white uppercase tracking-widest">
                  Red Flags ({result.red_flags.length})
                </h3>
              </div>

              <div className="space-y-4">
                {result.red_flags.map((flag) => (
                  <div
                    key={flag.id}
                    className="p-5 rounded-2xl bg-white/5 border-l-4 border-red-500/50 border-y border-r border-white/5"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={cn(
                            "px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest",
                            flag.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                              flag.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                                flag.severity === 'medium' ? 'bg-amber-500/20 text-amber-400' :
                                  'bg-white/10 text-slate-400'
                          )}>
                            {flag.severity.toUpperCase()}
                          </span>
                          <span className="font-bold text-white">{flag.rule}</span>
                        </div>
                        <p className="text-sm text-slate-400 mb-2">{flag.explanation}</p>
                        {flag.market_context && (
                          <p className="text-xs text-slate-500 mb-2">{flag.market_context}</p>
                        )}
                        <p className="text-sm font-bold text-gold">{flag.recommendation}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Strong Points */}
          {result.favorable_terms.length > 0 && (
            <Card className="liquid-glass p-8 border-emerald-500/20">
              <div className="flex items-center space-x-3 mb-6">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <h3 className="text-xl font-bold text-white uppercase tracking-widest">
                  Strong Points ({result.favorable_terms.length})
                </h3>
              </div>

              <div className="space-y-4">
                {result.favorable_terms.map((term) => (
                  <div
                    key={term.id}
                    className="p-5 rounded-2xl bg-white/5 border border-emerald-500/10"
                  >
                    <div className="flex items-start space-x-3">
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h4 className="font-bold text-white mb-1">{term.term}</h4>
                        <p className="text-sm text-slate-400 mb-2">{term.explanation}</p>
                        {term.market_context && (
                          <p className="text-xs text-slate-500">{term.market_context}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Negotiation Playbook */}
          {result.negotiation_points.length > 0 && (
            <Card className="liquid-glass p-8 border-gold/10">
              <div className="flex items-center space-x-3 mb-6">
                <Target className="w-5 h-5 text-gold" />
                <h3 className="text-xl font-bold text-white uppercase tracking-widest">
                  Negotiation Playbook
                </h3>
              </div>

              <div className="space-y-6">
                {result.negotiation_points
                  .sort((a, b) => a.priority - b.priority)
                  .map((point) => (
                    <div
                      key={point.id}
                      className="p-6 rounded-2xl bg-white/5 border border-white/5"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-3">
                            <span className="px-2 py-0.5 bg-gold/20 text-gold text-[10px] font-black uppercase tracking-widest rounded">
                              Priority #{point.priority}
                            </span>
                            <h4 className="font-bold text-white">{point.topic}</h4>
                          </div>
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div className="p-3 rounded-xl bg-white/5">
                              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Current</p>
                              <p className="text-sm text-slate-300">{point.current_term}</p>
                            </div>
                            <div className="p-3 rounded-xl bg-gold/5 border border-gold/10">
                              <p className="text-[10px] text-gold uppercase font-bold tracking-widest mb-1">Target</p>
                              <p className="text-sm text-gold font-bold">{point.target_term}</p>
                            </div>
                          </div>
                          <p className="text-sm text-slate-400 mb-3">{point.rationale}</p>
                          <div className="flex items-center space-x-2 mb-4">
                            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Success Rate:</span>
                            <span className="text-sm font-bold text-gold">{point.success_probability}</span>
                          </div>
                        </div>
                      </div>

                      <div className="bg-black/50 rounded-2xl p-5 border border-white/5">
                        <div className="flex items-center justify-between mb-3">
                          <span className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">
                            Email Script
                          </span>
                          <button
                            onClick={() => copyScript(point.script, point.id)}
                            className="h-7 px-3 text-xs font-bold rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-slate-400 hover:text-gold flex items-center space-x-1 transition-colors"
                          >
                            {copiedScript === point.id ? (
                              <>
                                <Check className="w-3 h-3" />
                                <span>Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span>Copy</span>
                              </>
                            )}
                          </button>
                        </div>
                        <p className="text-sm text-slate-400 whitespace-pre-wrap font-mono leading-relaxed">
                          {point.script}
                        </p>
                      </div>

                      {point.fallback && (
                        <div className="mt-4 text-xs text-slate-500">
                          <span className="font-bold text-gold">Fallback:</span> {point.fallback}
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            </Card>
          )}

          {/* AI Insights */}
          {result.narration && (
            <Card className="liquid-glass p-8 border-gold/10">
              <div className="flex items-center space-x-3 mb-4">
                <Lightbulb className="w-5 h-5 text-gold" />
                <h3 className="text-xl font-bold text-white uppercase tracking-widest">AI Insights</h3>
              </div>
              <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                {result.narration.summary}
              </p>
              <div className="mt-6 flex items-center space-x-4 text-xs text-slate-500 font-bold uppercase tracking-widest">
                <span>Confidence: {(result.narration.confidence * 100).toFixed(0)}%</span>
                <span className="text-white/10">|</span>
                <span>Model: {result.narration.model}</span>
              </div>
            </Card>
          )}

          {/* Actions */}
          <div className="flex items-center justify-center space-x-4">
            <button
              onClick={() => {
                setResult(null);
                setFile(null);
              }}
              className="px-6 py-3 rounded-2xl border border-white/10 bg-white/5 text-slate-300 hover:text-gold hover:border-gold/30 font-bold text-sm uppercase tracking-widest transition-all"
            >
              Analyze Another Contract
            </button>
            <button
              onClick={() => {
                console.log('Download report');
              }}
              className="btn-primary px-6 py-3 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download Report PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
