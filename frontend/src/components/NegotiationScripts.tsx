import { motion } from 'framer-motion'
import { Copy, CheckCircle2, MessageSquare } from 'lucide-react'
import { NegotiationScript } from '../types'

interface NegotiationScriptsProps {
  scripts: NegotiationScript[]
  onCopy: (text: string, index: number) => void
  copiedIndex: number | null
}

const NegotiationScripts = ({ scripts, onCopy, copiedIndex }: NegotiationScriptsProps) => {
  const getProbabilityColor = (prob: number) => {
    if (prob >= 0.7) return 'text-green-400'
    if (prob >= 0.5) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getProbabilityBg = (prob: number) => {
    if (prob >= 0.7) return 'bg-green-500/20 border-green-500/50'
    if (prob >= 0.5) return 'bg-yellow-500/20 border-yellow-500/50'
    return 'bg-red-500/20 border-red-500/50'
  }

  // Helper to get clause name (handles both old and new format)
  const getClauseName = (script: NegotiationScript) => {
    return script.clause || script.topic || 'Negotiation Point'
  }

  // Helper to get success probability (handles both old and new format)
  const getSuccessProbability = (script: NegotiationScript) => {
    if (typeof script.successProbability === 'number') {
      return script.successProbability
    }
    // Default probability if not provided
    return 0.6
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-2xl p-6"
    >
      <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <MessageSquare className="w-5 h-5 text-gold-500" />
        Negotiation Scripts
      </h3>
      
      <div className="space-y-4">
        {scripts.map((script, index) => {
          const clauseName = getClauseName(script)
          const probability = getSuccessProbability(script)
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-dark-700 rounded-lg p-5 border border-dark-600"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-gold-500 mb-1">{clauseName}</h4>
                  <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs border ${getProbabilityBg(probability)}`}>
                    <span className={getProbabilityColor(probability)}>
                      {Math.round(probability * 100)}% Success Probability
                    </span>
                  </div>
                </div>
                <motion.button
                  onClick={() => onCopy(script.script, index)}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  className="p-2 hover:bg-dark-600 rounded-lg transition-colors group cursor-pointer"
                  title="Copy script"
                >
                  {copiedIndex === index ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  ) : (
                    <Copy className="w-5 h-5 text-gray-400 group-hover:text-gold-500" />
                  )}
                </motion.button>
              </div>
              <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                "{script.script}"
              </p>
              {script.reason && (
                <p className="text-xs text-gray-500 mt-2 italic">
                  Reason: {script.reason}
                </p>
              )}
            </motion.div>
          )
        })}
      </div>

      <div className="mt-6 pt-6 border-t border-dark-600">
        <p className="text-xs text-gray-400">
          These scripts are AI-generated suggestions based on market analysis. 
          Customize them to match your communication style and situation.
        </p>
      </div>
    </motion.div>
  )
}

export default NegotiationScripts

