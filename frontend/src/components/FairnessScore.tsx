import { motion } from 'framer-motion'
import { TrendingUp } from 'lucide-react'

interface FairnessScoreProps {
  score: number
}

const FairnessScore = ({ score }: FairnessScoreProps) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-500/20 border-green-500/50'
    if (score >= 60) return 'bg-yellow-500/20 border-yellow-500/50'
    return 'bg-red-500/20 border-red-500/50'
  }

  const circumference = 2 * Math.PI * 90
  const offset = circumference - (score / 100) * circumference

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-effect rounded-2xl p-8 md:p-12"
    >
      <div className="flex flex-col md:flex-row items-center gap-8">
        <div className="relative w-48 h-48 flex-shrink-0">
          <svg className="transform -rotate-90 w-48 h-48">
            <circle
              cx="96"
              cy="96"
              r="90"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              className="text-dark-600"
            />
            <motion.circle
              cx="96"
              cy="96"
              r="90"
              stroke="currentColor"
              strokeWidth="12"
              fill="none"
              strokeLinecap="round"
              className={getScoreColor(score)}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              strokeDasharray={circumference}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5, type: "spring" }}
              className="text-center"
            >
              <div className={`text-5xl font-bold ${getScoreColor(score)}`}>
                {score}
              </div>
              <div className="text-sm text-gray-400">Fairness</div>
            </motion.div>
          </div>
        </div>

        <div className="flex-1">
          <h2 className="text-3xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-8 h-8 text-gold-500" />
            Contract Fairness Score
          </h2>
          <p className="text-gray-300 mb-6">
            Your contract has been analyzed against {Math.floor(Math.random() * 500 + 1000)} similar contracts 
            in the Indian market. The score reflects how your terms compare to industry standards.
          </p>
          <div className={`inline-block px-4 py-2 rounded-lg border ${getScoreBg(score)}`}>
            <span className={`text-sm font-semibold ${getScoreColor(score)}`}>
              {score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Needs Improvement'}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default FairnessScore

