import { motion } from 'framer-motion'
import { CheckCircle2 } from 'lucide-react'

interface FavorableTermsProps {
  terms: (string | { term?: string; title?: string; explanation?: string })[]
}

const FavorableTerms = ({ terms }: FavorableTermsProps) => {
  const getTermText = (term: string | { term?: string; title?: string; explanation?: string }) => {
    if (typeof term === 'string') return term
    return term.term || term.title || 'Unknown term'
  }

  const getTermExplanation = (term: string | { term?: string; title?: string; explanation?: string }) => {
    if (typeof term === 'string') return null
    return term.explanation
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-effect rounded-2xl p-6 border-l-4 border-green-500"
    >
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-green-400">
        <CheckCircle2 className="w-5 h-5" />
        Favorable Terms
      </h3>
      <ul className="space-y-3">
        {terms.map((term, index) => {
          const termText = getTermText(term)
          const explanation = getTermExplanation(term)
          return (
            <motion.li
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start gap-3 p-3 bg-green-500/10 rounded-lg"
            >
              <span className="text-green-400 mt-1">✓</span>
              <div className="flex-1">
                <span className="text-gray-300 font-medium">{termText}</span>
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

export default FavorableTerms

