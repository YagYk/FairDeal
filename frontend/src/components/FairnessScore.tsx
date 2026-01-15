import { motion } from 'framer-motion'
import { TrendingUp, Info, ChevronRight } from 'lucide-react'
import { AnalysisResult } from '../types'

interface FairnessScoreProps {
  score: number
  result?: AnalysisResult
}

const FairnessScore = ({ score, result }: FairnessScoreProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400'
    if (score >= 60) return 'text-amber-400'
    return 'text-red-400'
  }

  const getScoreGradient = (score: number) => {
    if (score >= 80) return 'from-emerald-500 to-green-500'
    if (score >= 60) return 'from-amber-500 to-yellow-500'
    return 'from-red-500 to-rose-500'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-emerald-500/10 border-emerald-500/30'
    if (score >= 60) return 'bg-amber-500/10 border-amber-500/30'
    return 'bg-red-500/10 border-red-500/30'
  }

  const getScoreLabel = (score: number) => {
    if (score >= 80) return { text: 'Excellent', emoji: '✨' }
    if (score >= 60) return { text: 'Good', emoji: '👍' }
    if (score >= 40) return { text: 'Fair', emoji: '⚠️' }
    return { text: 'Needs Attention', emoji: '⚡' }
  }

  const circumference = 2 * Math.PI * 90
  const offset = circumference - (score / 100) * circumference
  const scoreLabel = getScoreLabel(score)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="liquid-glass rounded-3xl p-6 md:p-10 gradient-border relative overflow-hidden"
    >
      {/* Background Glow Effect */}
      <div className={`absolute top-0 right-0 w-64 h-64 rounded-full blur-[100px] opacity-20 bg-gradient-to-br ${getScoreGradient(score)}`} />
      
      <div className="relative flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
        {/* Score Circle */}
        <div className="relative flex-shrink-0">
          <div className="relative w-52 h-52 md:w-56 md:h-56">
            {/* Outer Glow Ring */}
            <div className={`absolute inset-0 rounded-full blur-md opacity-30 bg-gradient-to-r ${getScoreGradient(score)}`} />
            
            <svg className="transform -rotate-90 w-full h-full relative z-10">
              {/* Background Circle */}
              <circle
                cx="50%"
                cy="50%"
                r="90"
                stroke="currentColor"
                strokeWidth="10"
                fill="none"
                className="text-dark-700/50"
              />
              {/* Progress Circle */}
              <motion.circle
                cx="50%"
                cy="50%"
                r="90"
                stroke="url(#scoreGradient)"
                strokeWidth="12"
                fill="none"
                strokeLinecap="round"
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset: offset }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                strokeDasharray={circumference}
                className="score-ring"
              />
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" className={score >= 80 ? 'text-emerald-400' : score >= 60 ? 'text-amber-400' : 'text-red-400'} stopColor="currentColor" />
                  <stop offset="100%" className={score >= 80 ? 'text-green-400' : score >= 60 ? 'text-yellow-400' : 'text-rose-400'} stopColor="currentColor" />
                </linearGradient>
              </defs>
            </svg>
            
            {/* Center Content */}
            <div className="absolute inset-0 flex items-center justify-center z-20">
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
                className="text-center"
              >
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.7 }}
                  className={`text-6xl font-bold ${getScoreColor(score)}`}
                >
                  {score}
                </motion.div>
                <div className="text-sm text-gray-400 mt-1">out of 100</div>
              </motion.div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 text-center lg:text-left">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-center justify-center lg:justify-start gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gold-500/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-gold-400" />
              </div>
              <h2 className="text-2xl md:text-3xl font-bold text-white">
                Contract Fairness Score
              </h2>
            </div>
            
            <p className="text-gray-400 mb-6 max-w-xl leading-relaxed">
              {result?.similarContractsCount || result?.detailedExplanation?.data_sources?.total_contracts_in_knowledge_base ? (
                <>
                  Analyzed against <span className="text-white font-medium">
                    {result.similarContractsCount || result.detailedExplanation?.data_sources?.total_contracts_in_knowledge_base || 0}+ similar contracts
                  </span> in our knowledge base. This score reflects how your terms compare to market standards.
                </>
              ) : (
                <>
                  Your contract has been thoroughly analyzed. This score reflects how your terms compare to industry standards.
                </>
              )}
            </p>

            {/* Score Badge */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4">
              <motion.div 
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.5 }}
                className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full border ${getScoreBg(score)}`}
              >
                <span className="text-xl">{scoreLabel.emoji}</span>
                <span className={`text-sm font-semibold ${getScoreColor(score)}`}>
                  {scoreLabel.text}
                </span>
              </motion.div>

              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gold-400 transition-colors group"
              >
                <Info className="w-4 h-4" />
                <span>How is this calculated?</span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </motion.button>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  )
}

export default FairnessScore
