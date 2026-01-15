import { motion } from 'framer-motion'
import { CheckCircle2, Sparkles, ChevronRight } from 'lucide-react'
import { FavorableTerm } from '../types'

interface FavorableTermsProps {
  terms: FavorableTerm[]
}

const FavorableTerms = ({ terms }: FavorableTermsProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="liquid-glass rounded-2xl p-6 gradient-border"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>
          <span>Favorable Terms</span>
          <span className="ml-2 px-2.5 py-1 text-xs font-medium bg-emerald-500/10 text-emerald-400 rounded-full">
            {terms.length} Found
          </span>
        </h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {terms.map((term, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            whileHover={{ scale: 1.01, y: -2 }}
            className="group relative p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 hover:border-emerald-500/40 transition-all cursor-pointer overflow-hidden"
          >
            {/* Subtle Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            
            <div className="relative flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Sparkles className="w-4 h-4 text-emerald-400" />
              </div>
              
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-white mb-1 flex items-center gap-2">
                  {term.clause || term.title || 'Positive Term'}
                  <ChevronRight className="w-4 h-4 text-emerald-400 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                </h4>
                <p className="text-sm text-gray-400 line-clamp-2">
                  {term.explanation || term.description}
                </p>
                
                {term.benefit && (
                  <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs">
                    <CheckCircle2 className="w-3 h-3" />
                    {term.benefit}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-6 p-4 bg-dark-800/50 rounded-xl border border-white/5"
      >
        <p className="text-xs text-gray-400 leading-relaxed">
          <span className="text-emerald-400 font-medium">✨ Good news:</span> These terms in your contract are above average 
          or particularly beneficial compared to similar contracts in the market.
        </p>
      </motion.div>
    </motion.div>
  )
}

export default FavorableTerms
