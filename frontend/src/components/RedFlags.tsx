import { motion } from 'framer-motion'
import { AlertTriangle } from 'lucide-react'

interface RedFlagsProps {
  flags: (string | { issue?: string; title?: string; explanation?: string })[]
}

const RedFlags = ({ flags }: RedFlagsProps) => {
  const getFlagText = (flag: string | { issue?: string; title?: string; explanation?: string }) => {
    if (typeof flag === 'string') return flag
    return flag.issue || flag.title || 'Unknown issue'
  }

  const getFlagExplanation = (flag: string | { issue?: string; title?: string; explanation?: string }) => {
    if (typeof flag === 'string') return null
    return flag.explanation
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-2xl p-6 border-l-4 border-red-500"
    >
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-red-400">
        <AlertTriangle className="w-5 h-5" />
        Red Flags
      </h3>
      <ul className="space-y-3">
        {flags.map((flag, index) => {
          const flagText = getFlagText(flag)
          const explanation = getFlagExplanation(flag)
          return (
            <motion.li
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start gap-3 p-3 bg-red-500/10 rounded-lg"
            >
              <span className="text-red-400 mt-1">•</span>
              <div className="flex-1">
                <span className="text-gray-300 font-medium">{flagText}</span>
                {explanation && (
                  <p className="text-sm text-gray-400 mt-1">{explanation}</p>
                )}
              </div>
            </motion.li>
          )
        })}
      </ul>
    </motion.div>
  )
}

export default RedFlags

