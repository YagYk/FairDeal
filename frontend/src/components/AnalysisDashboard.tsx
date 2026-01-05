import { motion } from 'framer-motion'
import { ArrowLeft, TrendingUp } from 'lucide-react'
import { useState } from 'react'
import FairnessScore from './FairnessScore'
import PercentileCharts from './PercentileCharts'
import RedFlags from './RedFlags'
import FavorableTerms from './FavorableTerms'
import NegotiationScripts from './NegotiationScripts'
import Chatbot from './Chatbot'
import DetailedReport from './DetailedReport'
import { AnalysisResult } from '../types'

interface AnalysisDashboardProps {
  result: AnalysisResult
  analysisId?: string
  onReset: () => void
}

const AnalysisDashboard = ({ result, analysisId, onReset }: AnalysisDashboardProps) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-8 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <motion.button
          onClick={onReset}
          whileHover={{ scale: 1.05, x: -5 }}
          whileTap={{ scale: 0.95 }}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Analyze Another Contract</span>
        </motion.button>
      </motion.div>

      {/* Fairness Score */}
      <FairnessScore score={result.fairnessScore} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Percentile Charts */}
        <PercentileCharts rankings={result.percentileRankings} />

        {/* Contract Metadata */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-effect rounded-2xl p-6"
        >
          <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-gold-500" />
            Contract Details
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Type:</span>
              <span className="font-medium capitalize">{result.contractMetadata.contractType}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Industry:</span>
              <span className="font-medium capitalize">{result.contractMetadata.industry}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Role:</span>
              <span className="font-medium">{result.contractMetadata.role || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Location:</span>
              <span className="font-medium">{result.contractMetadata.location}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Salary:</span>
              <span className="font-medium">
                {result.contractMetadata.salary 
                  ? `₹${result.contractMetadata.salary.toLocaleString()}` 
                  : 'Not specified'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Notice Period:</span>
              <span className="font-medium">
                {result.contractMetadata.noticePeriodDays 
                  ? `${result.contractMetadata.noticePeriodDays} days` 
                  : 'Not specified'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Non-Compete:</span>
              <span className={`font-medium ${result.contractMetadata.nonCompete ? 'text-red-400' : 'text-green-400'}`}>
                {result.contractMetadata.nonCompete ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Red Flags */}
      {result.redFlags.length > 0 && (
        <RedFlags flags={result.redFlags} />
      )}

      {/* Favorable Terms */}
      {result.favorableTerms.length > 0 && (
        <FavorableTerms terms={result.favorableTerms} />
      )}

      {/* Negotiation Scripts */}
      <NegotiationScripts
        scripts={result.negotiationScripts}
        onCopy={handleCopy}
        copiedIndex={copiedIndex}
      />

      {/* Detailed Report */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <DetailedReport result={result} />
      </motion.div>

      {/* Chatbot */}
      {analysisId && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Chatbot analysisId={analysisId} />
        </motion.div>
      )}
    </div>
  )
}

export default AnalysisDashboard

