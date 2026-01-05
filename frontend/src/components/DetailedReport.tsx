import { motion } from 'framer-motion'
import { FileText, TrendingUp, AlertTriangle, CheckCircle, BarChart3, Database, Info } from 'lucide-react'
import { AnalysisResult } from '../types'

interface DetailedReportProps {
  result: AnalysisResult
}

const DetailedReport = ({ result }: DetailedReportProps) => {
  const explanation = result.detailedExplanation
  if (!explanation) return null

  return (
    <div className="space-y-6">
      {/* Data Sources Transparency */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-effect rounded-2xl p-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <Database className="w-6 h-6 text-gold-500" />
          <h3 className="text-xl font-semibold">Data Sources & Transparency</h3>
        </div>
        
        {explanation.data_sources && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-dark-700/50 rounded-lg p-4">
                <div className="text-2xl font-bold text-gold-400">
                  {explanation.data_sources.knowledge_base_contracts_used || 0}
                </div>
                <div className="text-sm text-gray-400">Contracts Used</div>
              </div>
              <div className="bg-dark-700/50 rounded-lg p-4">
                <div className="text-2xl font-bold text-gold-400">
                  {explanation.data_sources.total_contracts_in_knowledge_base || 0}
                </div>
                <div className="text-sm text-gray-400">Total in Database</div>
              </div>
              <div className="bg-dark-700/50 rounded-lg p-4">
                <div className="text-2xl font-bold text-gold-400">
                  {explanation.data_sources.data_quality?.coverage || 'N/A'}
                </div>
                <div className="text-sm text-gray-400">Coverage</div>
              </div>
              <div className="bg-dark-700/50 rounded-lg p-4">
                <div className="text-2xl font-bold text-gold-400">
                  {explanation.data_sources.data_quality?.relevance || 'N/A'}
                </div>
                <div className="text-sm text-gray-400">Relevance</div>
              </div>
            </div>

            {explanation.data_sources.similar_contracts_details && explanation.data_sources.similar_contracts_details.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-semibold text-gray-300 mb-2">Top Similar Contracts Used:</h4>
                <div className="space-y-2">
                  {explanation.data_sources.similar_contracts_details.slice(0, 5).map((contract: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between bg-dark-700/30 rounded-lg p-3 text-sm">
                      <div className="flex items-center gap-3">
                        <FileText className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-300">
                          {contract.contract_type || 'Unknown'} - {contract.industry || 'General'}
                        </span>
                      </div>
                      <div className="text-gold-400 font-medium">
                        {contract.similarity_score}% match
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </motion.div>

      {/* Fairness Score Explanation */}
      {explanation.explanations?.fairness_score_explanation && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className="w-6 h-6 text-gold-500" />
            <h3 className="text-xl font-semibold">Fairness Score Explanation</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="text-4xl font-bold text-gold-400">
                {explanation.explanations.fairness_score_explanation.score}%
              </div>
              <div>
                <div className="text-lg font-semibold">
                  {explanation.explanations.fairness_score_explanation.category}
                </div>
                <div className="text-sm text-gray-400">Overall Assessment</div>
              </div>
            </div>
            
            <p className="text-gray-300 leading-relaxed whitespace-pre-line">
              {explanation.explanations.fairness_score_explanation.explanation}
            </p>
            
            <div className="border-t border-dark-600 pt-4">
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Score Factors:</h4>
              <ul className="space-y-1">
                {explanation.explanations.fairness_score_explanation.factors?.map((factor: string, idx: number) => (
                  <li key={idx} className="text-sm text-gray-400 flex items-start gap-2">
                    <span className="text-gold-400 mt-1">•</span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      )}

      {/* Percentile Explanations */}
      {explanation.explanations?.percentile_explanations && Object.keys(explanation.explanations.percentile_explanations).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <BarChart3 className="w-6 h-6 text-gold-500" />
            <h3 className="text-xl font-semibold">Market Comparison Details</h3>
          </div>
          
          <div className="space-y-6">
            {Object.entries(explanation.explanations.percentile_explanations).map(([key, data]: [string, any]) => (
              <div key={key} className="border-l-2 border-gold-500/30 pl-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold capitalize">{key.replace('_', ' ')}</h4>
                  <div className="text-gold-400 font-bold">{data.percentile}th percentile</div>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                  <div>
                    <div className="text-xs text-gray-400">Your Value</div>
                    <div className="font-medium">{data.your_value}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Market Median</div>
                    <div className="font-medium">{data.market_comparison?.median}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Market Average</div>
                    <div className="font-medium">{data.market_comparison?.mean}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">75th Percentile</div>
                    <div className="font-medium">{data.market_comparison?.p75}</div>
                  </div>
                </div>
                
                <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-line">
                  {data.explanation}
                </p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Red Flags Explanations */}
      {explanation.explanations?.red_flags_explanations && explanation.explanations.red_flags_explanations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-red-400" />
            <h3 className="text-xl font-semibold">Red Flags - Detailed Analysis</h3>
          </div>
          
          <div className="space-y-4">
            {explanation.explanations.red_flags_explanations.map((flag: any) => (
              <div key={flag.flag_number} className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-red-400 font-bold">#{flag.flag_number}</span>
                      <h4 className="font-semibold">{flag.issue}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${
                        flag.severity === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {flag.severity} Severity
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 mb-2">{flag.explanation}</p>
                    <p className="text-xs text-gray-400">
                      <strong>Recommendation:</strong> {flag.recommendation}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Favorable Terms Explanations */}
      {explanation.explanations?.favorable_terms_explanations && explanation.explanations.favorable_terms_explanations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="w-6 h-6 text-green-400" />
            <h3 className="text-xl font-semibold">Favorable Terms - Detailed Analysis</h3>
          </div>
          
          <div className="space-y-4">
            {explanation.explanations.favorable_terms_explanations.map((term: any) => (
              <div key={term.term_number} className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-green-400 font-bold">#{term.term_number}</span>
                      <h4 className="font-semibold">{term.term}</h4>
                      <span className={`px-2 py-1 rounded text-xs ${
                        term.value === 'High' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {term.value} Value
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">{term.explanation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Negotiation Recommendations */}
      {explanation.explanations?.negotiation_recommendations && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-effect rounded-2xl p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Info className="w-6 h-6 text-blue-400" />
            <h3 className="text-xl font-semibold">Negotiation Recommendations</h3>
          </div>
          
          <div className="space-y-4">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 mb-4">
              <p className="font-semibold text-lg mb-2">
                {explanation.explanations.negotiation_recommendations.overall_advice}
              </p>
              <p className="text-sm text-gray-300">
                {explanation.explanations.negotiation_recommendations.should_negotiate
                  ? "Based on our analysis, we recommend negotiating the following items:"
                  : "Your contract is generally fair and competitive."}
              </p>
            </div>
            
            {explanation.explanations.negotiation_recommendations.recommendations?.map((rec: any, idx: number) => (
              <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">{rec.item}</h4>
                  <span className={`px-2 py-1 rounded text-xs ${
                    rec.priority === 'High' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {rec.priority} Priority
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-2">
                  <div>
                    <div className="text-xs text-gray-400">Current</div>
                    <div className="font-medium">{rec.current}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">Recommended</div>
                    <div className="font-medium text-gold-400">{rec.recommended}</div>
                  </div>
                </div>
                <p className="text-sm text-gray-300">{rec.reason}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Overall Assessment */}
      {explanation.explanations?.overall_assessment && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-effect rounded-2xl p-6 bg-gradient-to-br from-dark-800 to-dark-900"
        >
          <h3 className="text-xl font-semibold mb-4">Overall Assessment</h3>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="text-3xl font-bold text-gold-400">
                {explanation.explanations.overall_assessment.assessment}
              </div>
              <div className="flex-1">
                <div className="text-sm text-gray-400 mb-1">Signing Recommendation</div>
                <div className="text-lg font-semibold">
                  {explanation.explanations.overall_assessment.signing_recommendation}
                </div>
              </div>
            </div>
            <p className="text-gray-300 leading-relaxed whitespace-pre-line">
              {explanation.explanations.overall_assessment.summary}
            </p>
          </div>
        </motion.div>
      )}

      {/* Confidence Metrics */}
      {explanation.confidence_metrics && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="glass-effect rounded-2xl p-6"
        >
          <h3 className="text-xl font-semibold mb-4">Analysis Confidence</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <div className="text-2xl font-bold text-gold-400">
                {explanation.confidence_metrics.confidence_level}
              </div>
              <div className="text-sm text-gray-400">Confidence Level</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gold-400">
                {explanation.confidence_metrics.sample_size}
              </div>
              <div className="text-sm text-gray-400">Sample Size</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-gold-400">
                {explanation.confidence_metrics.data_quality}
              </div>
              <div className="text-sm text-gray-400">Data Quality</div>
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-4">
            {explanation.confidence_metrics.explanation}
          </p>
        </motion.div>
      )}
    </div>
  )
}

export default DetailedReport

