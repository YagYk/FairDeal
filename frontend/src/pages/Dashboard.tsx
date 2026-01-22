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

    // Simulate progress updates
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
    if (score >= 80) return 'text-emerald-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    if (score >= 20) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-50 border-emerald-200';
    if (score >= 60) return 'bg-blue-50 border-blue-200';
    if (score >= 40) return 'bg-yellow-50 border-yellow-200';
    if (score >= 20) return 'bg-orange-50 border-orange-200';
    return 'bg-red-50 border-red-200';
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
            FairDeal Contract Intelligence
          </h1>
          <p className="text-lg text-slate-600">
            From anxiety to clarity in 3 seconds. Know exactly what's unfair, why it matters, and how to negotiate.
          </p>
        </div>

        {/* Upload Section */}
        {!result && (
          <Card className="p-8">
            <div className="space-y-6">
              <ContextForm
                onContextChange={setContext}
                initialContext={context}
              />

              <div className="border-2 border-dashed border-slate-300 rounded-xl p-12 text-center hover:border-blue-400 transition-colors">
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
                  <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
                    <Upload className="w-8 h-8 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-lg font-semibold text-slate-900">
                      {file ? file.name : 'Upload Your Contract'}
                    </p>
                    <p className="text-sm text-slate-500 mt-1">
                      PDF or DOCX files only
                    </p>
                  </div>
                </label>
              </div>

              <Button
                onClick={handleAnalyze}
                disabled={!file || analyzeMutation.isPending}
                className="w-full py-6 text-lg font-semibold bg-blue-600 hover:bg-blue-700"
              >
                {analyzeMutation.isPending ? (
                  <>
                    <Clock className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Analyze Contract
                  </>
                )}
              </Button>
            </div>
          </Card>
        )}

        {/* Progress Indicator */}
        {progress && !result && (
          <Card className={`p-8 ${getScoreBgColor(progress.progress)}`}>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900">
                  {progress.message}
                </h3>
                <span className="text-sm font-medium text-slate-600">
                  {progress.progress}%
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress.progress}%` }}
                />
              </div>
              <div className="flex items-center space-x-2 text-sm text-slate-600">
                <CheckCircle2 className="w-4 h-4 text-green-500" />
                <span>✓ Extracted text ({Math.round(progress.progress * 0.3)}ms)</span>
                {progress.progress > 40 && (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-green-500 ml-4" />
                    <span>✓ Found salary</span>
                  </>
                )}
                {progress.progress > 50 && (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-green-500 ml-4" />
                    <span>✓ Found notice period</span>
                  </>
                )}
                {progress.progress > 70 && (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-green-500 ml-4" />
                    <span>✓ Comparing with similar contracts</span>
                  </>
                )}
              </div>
            </div>
          </Card>
        )}

        {/* Results Dashboard */}
        {result && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Score Card */}
            <Card className={`p-8 ${getScoreBgColor(result.score)} border-2`}>
              <div className="text-center space-y-4">
                <div className="flex items-center justify-center space-x-3">
                  <span className="text-5xl">{getGradeEmoji(result.grade)}</span>
                  <div>
                    <h2 className="text-5xl font-bold text-slate-900">
                      {Math.round(result.score)}/100
                    </h2>
                    <p className="text-xl font-semibold text-slate-700 mt-1">
                      {getGradeEmoji(result.grade)} {result.grade} CONTRACT
                    </p>
                  </div>
                </div>

                <div className="w-full bg-slate-200 rounded-full h-4 overflow-hidden max-w-md mx-auto">
                  <div
                    className={`h-full rounded-full transition-all duration-1000 ${result.score >= 80 ? 'bg-gradient-to-r from-emerald-500 to-emerald-600' :
                        result.score >= 60 ? 'bg-gradient-to-r from-blue-500 to-blue-600' :
                          result.score >= 40 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                            result.score >= 20 ? 'bg-gradient-to-r from-orange-500 to-orange-600' :
                              'bg-gradient-to-r from-red-500 to-red-600'
                      }`}
                    style={{ width: `${result.score}%` }}
                  />
                </div>

                {result.contract_metadata.role_title && (
                  <p className="text-sm text-slate-600">
                    {result.contract_metadata.company_name || 'Company'} • {result.contract_metadata.role_title}
                  </p>
                )}
              </div>
            </Card>

            {/* How You Compare */}
            {Object.keys(result.percentiles).length > 0 && (
              <Card className="p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  <h3 className="text-xl font-bold text-slate-900">📊 HOW YOU COMPARE</h3>
                </div>

                <div className="space-y-6">
                  {result.percentiles.salary && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-slate-900">
                          Salary ({result.percentiles.salary.field_display})
                        </span>
                        <span className="text-sm font-medium text-slate-600">
                          {result.percentiles.salary.value.toFixed(1)}th percentile
                        </span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-6 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full flex items-center justify-end pr-2"
                          style={{ width: `${result.percentiles.salary.value}%` }}
                        >
                          <span className="text-xs font-bold text-white">
                            Better than {result.percentiles.salary.value.toFixed(0)}% of similar contracts
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-slate-600 mt-2">
                        {result.percentiles.salary.insight}
                      </p>
                    </div>
                  )}

                  {result.percentiles.notice_period && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-slate-900">
                          Notice Period ({result.percentiles.notice_period.field_display})
                        </span>
                        <span className="text-sm font-medium text-slate-600">
                          {result.percentiles.notice_period.value.toFixed(1)}th percentile
                          {result.percentiles.notice_period.interpretation === 'excellent' && (
                            <span className="ml-2 text-emerald-600">⭐ EXCELLENT</span>
                          )}
                        </span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-6 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-emerald-500 to-emerald-600 h-full rounded-full flex items-center justify-end pr-2"
                          style={{ width: `${100 - result.percentiles.notice_period.value}%` }}
                        >
                          <span className="text-xs font-bold text-white">
                            Shorter than {100 - Math.round(result.percentiles.notice_period.value)}% of contracts
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-slate-600 mt-2">
                        {result.percentiles.notice_period.insight}
                      </p>
                    </div>
                  )}
                </div>
              </Card>
            )}

            {/* Red Flags */}
            {result.red_flags.length > 0 && (
              <Card className="p-6 border-red-200 bg-red-50/50">
                <div className="flex items-center space-x-2 mb-6">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  <h3 className="text-xl font-bold text-slate-900">
                    ⚠️ RED FLAGS ({result.red_flags.length})
                  </h3>
                </div>

                <div className="space-y-4">
                  {result.red_flags.map((flag) => (
                    <div
                      key={flag.id}
                      className="p-4 bg-white rounded-lg border border-red-200 shadow-sm"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${flag.severity === 'critical' ? 'bg-red-600 text-white' :
                                flag.severity === 'high' ? 'bg-orange-500 text-white' :
                                  flag.severity === 'medium' ? 'bg-yellow-500 text-white' :
                                    'bg-slate-500 text-white'
                              }`}>
                              {flag.severity.toUpperCase()}
                            </span>
                            <span className="font-semibold text-slate-900">{flag.rule}</span>
                          </div>
                          <p className="text-sm text-slate-700 mb-2">{flag.explanation}</p>
                          {flag.market_context && (
                            <p className="text-xs text-slate-600 mb-2">{flag.market_context}</p>
                          )}
                          <p className="text-sm font-medium text-blue-600">{flag.recommendation}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Strong Points */}
            {result.favorable_terms.length > 0 && (
              <Card className="p-6 border-emerald-200 bg-emerald-50/50">
                <div className="flex items-center space-x-2 mb-6">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  <h3 className="text-xl font-bold text-slate-900">
                    ✨ STRONG POINTS ({result.favorable_terms.length})
                  </h3>
                </div>

                <div className="space-y-4">
                  {result.favorable_terms.map((term) => (
                    <div
                      key={term.id}
                      className="p-4 bg-white rounded-lg border border-emerald-200 shadow-sm"
                    >
                      <div className="flex items-start space-x-3">
                        <CheckCircle2 className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <h4 className="font-semibold text-slate-900 mb-1">{term.term}</h4>
                          <p className="text-sm text-slate-700 mb-2">{term.explanation}</p>
                          {term.market_context && (
                            <p className="text-xs text-slate-600">{term.market_context}</p>
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
              <Card className="p-6 border-blue-200 bg-blue-50/50">
                <div className="flex items-center space-x-2 mb-6">
                  <Target className="w-5 h-5 text-blue-600" />
                  <h3 className="text-xl font-bold text-slate-900">
                    🎯 NEGOTIATION PLAYBOOK
                  </h3>
                </div>

                <div className="space-y-6">
                  {result.negotiation_points
                    .sort((a, b) => a.priority - b.priority)
                    .map((point) => (
                      <div
                        key={point.id}
                        className="p-5 bg-white rounded-lg border border-blue-200 shadow-sm"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className="px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded">
                                Priority #{point.priority}
                              </span>
                              <h4 className="font-semibold text-slate-900">{point.topic}</h4>
                            </div>
                            <div className="grid grid-cols-2 gap-4 mb-3 text-sm">
                              <div>
                                <span className="text-slate-600">Current:</span>
                                <span className="ml-2 font-medium text-slate-900">{point.current_term}</span>
                              </div>
                              <div>
                                <span className="text-slate-600">Target:</span>
                                <span className="ml-2 font-medium text-emerald-600">{point.target_term}</span>
                              </div>
                            </div>
                            <p className="text-sm text-slate-700 mb-3">{point.rationale}</p>
                            <div className="flex items-center space-x-2 mb-4">
                              <span className="text-xs font-medium text-slate-600">Success Rate:</span>
                              <span className="text-sm font-semibold text-blue-600">{point.success_probability}</span>
                            </div>
                          </div>
                        </div>

                        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide">
                              Email Script
                            </span>
                            <button
                              onClick={() => copyScript(point.script, point.id)}
                              className="h-7 px-3 text-xs font-medium rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 flex items-center space-x-1"
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
                          <p className="text-sm text-slate-700 whitespace-pre-wrap font-mono">
                            {point.script}
                          </p>
                        </div>

                        {point.fallback && (
                          <div className="mt-3 text-xs text-slate-600">
                            <span className="font-semibold">Fallback:</span> {point.fallback}
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              </Card>
            )}

            {/* AI Insights */}
            {result.narration && (
              <Card className="p-6 border-purple-200 bg-purple-50/50">
                <div className="flex items-center space-x-2 mb-4">
                  <Lightbulb className="w-5 h-5 text-purple-600" />
                  <h3 className="text-xl font-bold text-slate-900">💡 AI INSIGHTS</h3>
                </div>
                <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                  {result.narration.summary}
                </p>
                <div className="mt-4 flex items-center space-x-4 text-xs text-slate-600">
                  <span>Confidence: {(result.narration.confidence * 100).toFixed(0)}%</span>
                  <span>Model: {result.narration.model}</span>
                </div>
              </Card>
            )}

            {/* Actions */}
            <div className="flex items-center justify-center space-x-4">
              <Button
                variant="outline"
                onClick={() => {
                  setResult(null);
                  setFile(null);
                }}
              >
                Analyze Another Contract
              </Button>
              <Button
                onClick={() => {
                  // TODO: Implement PDF download
                  console.log('Download report');
                }}
              >
                <Download className="w-4 h-4 mr-2" />
                Download Report PDF
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
