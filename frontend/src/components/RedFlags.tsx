import { motion } from 'framer-motion'
import { AlertTriangle, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { RedFlag } from '../types'

interface RedFlagsProps {
  flags: RedFlag[]
}

const RedFlags = ({ flags }: RedFlagsProps) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  const getSeverityConfig = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return {
          icon: AlertTriangle,
          color: 'text-red-400',
          bgColor: 'bg-red-500/10',
          borderColor: 'border-red-500/30',
          label: 'High Risk',
          gradient: 'from-red-500/20 to-transparent',
        }
      case 'medium':
        return {
          icon: AlertCircle,
          color: 'text-amber-400',
          bgColor: 'bg-amber-500/10',
          borderColor: 'border-amber-500/30',
          label: 'Medium Risk',
          gradient: 'from-amber-500/20 to-transparent',
        }
      default:
        return {
          icon: Info,
          color: 'text-blue-400',
          bgColor: 'bg-blue-500/10',
          borderColor: 'border-blue-500/30',
          label: 'Low Risk',
          gradient: 'from-blue-500/20 to-transparent',
        }
    }
  }

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="liquid-glass rounded-2xl p-6 gradient-border"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-red-500/10 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-red-400" />
          </div>
          <span>Red Flags</span>
          <span className="ml-2 px-2.5 py-1 text-xs font-medium bg-red-500/10 text-red-400 rounded-full">
            {flags.length} Found
          </span>
        </h3>
      </div>

      <div className="space-y-4">
        {flags.map((flag, index) => {
          const config = getSeverityConfig(flag.severity)
          const Icon = config.icon
          const isExpanded = expandedIndex === index

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`relative rounded-xl border ${config.borderColor} overflow-hidden`}
            >
              {/* Background Gradient */}
              <div className={`absolute inset-0 bg-gradient-to-r ${config.gradient} pointer-events-none`} />
              
              <div 
                className={`relative p-4 cursor-pointer ${config.bgColor} hover:bg-opacity-80 transition-all`}
                onClick={() => toggleExpand(index)}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-lg ${config.bgColor} flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-5 h-5 ${config.color}`} />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h4 className="font-semibold text-white">{flag.clause || flag.title || 'Potential Issue'}</h4>
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${config.bgColor} ${config.color}`}>
                        {config.label}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 line-clamp-2">
                      {flag.explanation || flag.description}
                    </p>
                  </div>

                  <button className={`p-2 rounded-lg ${config.bgColor} transition-colors flex-shrink-0`}>
                    {isExpanded ? (
                      <ChevronUp className={`w-5 h-5 ${config.color}`} />
                    ) : (
                      <ChevronDown className={`w-5 h-5 ${config.color}`} />
                    )}
                  </button>
                </div>

                {/* Expanded Content */}
                <motion.div
                  initial={false}
                  animate={{ 
                    height: isExpanded ? 'auto' : 0,
                    opacity: isExpanded ? 1 : 0
                  }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-white/5 space-y-3">
                      {flag.source_text && (
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Source Text</p>
                          <p className="text-sm text-gray-300 bg-dark-800/50 p-3 rounded-lg italic">
                            "{flag.source_text}"
                          </p>
                        </div>
                      )}
                      {flag.recommendation && (
                        <div>
                          <p className="text-xs text-gray-500 mb-1">Recommendation</p>
                          <p className="text-sm text-gray-300">{flag.recommendation}</p>
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-6 p-4 bg-dark-800/50 rounded-xl border border-white/5"
      >
        <p className="text-xs text-gray-400 leading-relaxed">
          <span className="text-red-400 font-medium">⚠️ Important:</span> These are potential concerns identified in your contract. 
          Consider discussing these points during negotiation or consulting with a legal professional.
        </p>
      </motion.div>
    </motion.div>
  )
}

export default RedFlags
