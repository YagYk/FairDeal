import { motion } from 'framer-motion'
import { ArrowLeft, TrendingUp, FileText, MapPin, Briefcase, Building2, DollarSign, Clock, Shield } from 'lucide-react'
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

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  }

  const metadataItems = [
    { 
      icon: FileText, 
      label: 'Contract Type', 
      value: result.contractMetadata.contractType,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10'
    },
    { 
      icon: Building2, 
      label: 'Industry', 
      value: result.contractMetadata.industry,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10'
    },
    { 
      icon: Briefcase, 
      label: 'Role', 
      value: result.contractMetadata.role || 'Not specified',
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10'
    },
    { 
      icon: MapPin, 
      label: 'Location', 
      value: result.contractMetadata.location,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10'
    },
    { 
      icon: DollarSign, 
      label: 'Salary', 
      value: result.contractMetadata.salary 
        ? `₹${result.contractMetadata.salary.toLocaleString()}` 
        : 'Not specified',
      color: 'text-gold-400',
      bgColor: 'bg-gold-500/10'
    },
    { 
      icon: Clock, 
      label: 'Notice Period', 
      value: result.contractMetadata.noticePeriodDays 
        ? `${result.contractMetadata.noticePeriodDays} days` 
        : 'Not specified',
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10'
    },
  ]

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8"
    >
      {/* Header */}
      <motion.div
        variants={itemVariants}
        className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <motion.button
          onClick={onReset}
          whileHover={{ scale: 1.02, x: -3 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors cursor-pointer group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span>Analyze Another Contract</span>
        </motion.button>
        
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          Analysis Complete
        </div>
      </motion.div>

      {/* Fairness Score */}
      <motion.div variants={itemVariants}>
        <FairnessScore score={result.fairnessScore} result={result} />
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Percentile Charts */}
        <motion.div variants={itemVariants}>
          <PercentileCharts rankings={result.percentileRankings} />
        </motion.div>

        {/* Contract Metadata */}
        <motion.div
          variants={itemVariants}
          className="liquid-glass rounded-2xl p-6 gradient-border"
        >
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gold-500/10 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-gold-400" />
            </div>
            <span>Contract Details</span>
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {metadataItems.map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
                className="flex items-center gap-3 p-3 rounded-xl bg-dark-800/50 hover:bg-dark-700/50 transition-colors"
              >
                <div className={`w-10 h-10 rounded-lg ${item.bgColor} flex items-center justify-center flex-shrink-0`}>
                  <item.icon className={`w-5 h-5 ${item.color}`} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-gray-500 mb-0.5">{item.label}</p>
                  <p className="text-sm font-medium text-white truncate capitalize">{item.value}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Non-Compete Badge */}
          <div className="mt-4 pt-4 border-t border-white/5">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
              result.contractMetadata.nonCompete 
                ? 'bg-red-500/10 border border-red-500/20' 
                : 'bg-green-500/10 border border-green-500/20'
            }`}>
              <Shield className={`w-4 h-4 ${result.contractMetadata.nonCompete ? 'text-red-400' : 'text-green-400'}`} />
              <span className={`text-sm font-medium ${result.contractMetadata.nonCompete ? 'text-red-400' : 'text-green-400'}`}>
                Non-Compete: {result.contractMetadata.nonCompete ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Red Flags */}
      {result.redFlags.length > 0 && (
        <motion.div variants={itemVariants}>
          <RedFlags flags={result.redFlags} />
        </motion.div>
      )}

      {/* Favorable Terms */}
      {result.favorableTerms.length > 0 && (
        <motion.div variants={itemVariants}>
          <FavorableTerms terms={result.favorableTerms} />
        </motion.div>
      )}

      {/* Negotiation Scripts */}
      <motion.div variants={itemVariants}>
        <NegotiationScripts
          scripts={result.negotiationScripts}
          onCopy={handleCopy}
          copiedIndex={copiedIndex}
        />
      </motion.div>

      {/* Detailed Report */}
      <motion.div variants={itemVariants}>
        <DetailedReport result={result} />
      </motion.div>

      {/* Chatbot */}
      {analysisId && (
        <motion.div variants={itemVariants}>
          <Chatbot analysisId={analysisId} />
        </motion.div>
      )}
    </motion.div>
  )
}

export default AnalysisDashboard
