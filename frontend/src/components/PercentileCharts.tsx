import { motion } from 'framer-motion'
import { BarChart3, TrendingUp, TrendingDown, Minus, DollarSign, Clock } from 'lucide-react'
import { PercentileRankings } from '../types'

interface PercentileChartsProps {
  rankings: PercentileRankings
}

const PercentileCharts = ({ rankings }: PercentileChartsProps) => {
  const getPercentileInfo = (percentile: number | null, isHigherBetter: boolean) => {
    if (percentile === null) return { color: 'text-gray-500', bg: 'bg-gray-500', label: 'N/A', icon: Minus }
    
    const isGood = isHigherBetter ? percentile >= 50 : percentile <= 50
    
    if (isGood) {
      return {
        color: 'text-emerald-400',
        bg: 'bg-emerald-500',
        gradient: 'from-emerald-500 to-green-500',
        label: percentile >= 75 ? 'Excellent' : 'Good',
        icon: TrendingUp,
      }
    } else {
      return {
        color: 'text-amber-400',
        bg: 'bg-amber-500',
        gradient: 'from-amber-500 to-orange-500',
        label: percentile <= 25 ? 'Below Average' : 'Fair',
        icon: TrendingDown,
      }
    }
  }

  const metrics = [
    {
      key: 'salary',
      label: 'Salary',
      icon: DollarSign,
      value: rankings.salary,
      isHigherBetter: true,
      description: 'Compared to similar roles',
    },
    {
      key: 'notice',
      label: 'Notice Period',
      icon: Clock,
      value: rankings.noticePeriod,
      isHigherBetter: false,
      description: 'Lower is generally better',
    },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="liquid-glass rounded-2xl p-6 gradient-border h-full"
    >
      <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
          <BarChart3 className="w-5 h-5 text-blue-400" />
        </div>
        <span>Market Position</span>
      </h3>

      <div className="space-y-6">
        {metrics.map((metric, index) => {
          const info = getPercentileInfo(metric.value, metric.isHigherBetter)
          const Icon = metric.icon
          const TrendIcon = info.icon
          
          return (
            <motion.div
              key={metric.key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="space-y-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-lg ${metric.isHigherBetter ? 'bg-gold-500/10' : 'bg-purple-500/10'} flex items-center justify-center`}>
                    <Icon className={`w-5 h-5 ${metric.isHigherBetter ? 'text-gold-400' : 'text-purple-400'}`} />
                  </div>
                  <div>
                    <span className="text-white font-medium">{metric.label}</span>
                    <p className="text-xs text-gray-500">{metric.description}</p>
                  </div>
                </div>
                <div className="text-right flex items-center gap-2">
                  {metric.value !== null ? (
                    <>
                      <TrendIcon className={`w-4 h-4 ${info.color}`} />
                      <span className={`text-lg font-bold ${info.color}`}>
                        {metric.value}%
                      </span>
                    </>
                  ) : (
                    <span className="text-gray-500">Not available</span>
                  )}
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="relative">
                <div className="h-3 bg-dark-700/50 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: metric.value !== null ? `${metric.value}%` : '0%' }}
                    transition={{ duration: 1, delay: 0.3 + index * 0.1, ease: "easeOut" }}
                    className={`h-full rounded-full bg-gradient-to-r ${info.gradient || 'from-gray-500 to-gray-600'}`}
                  />
                </div>
                
                {/* Percentile Markers */}
                <div className="absolute top-0 left-0 right-0 h-3 flex items-center pointer-events-none">
                  <div className="absolute left-1/4 w-px h-full bg-white/10" />
                  <div className="absolute left-1/2 w-px h-full bg-white/20" />
                  <div className="absolute left-3/4 w-px h-full bg-white/10" />
                </div>
              </div>
              
              {/* Labels */}
              <div className="flex justify-between text-xs text-gray-500">
                <span>0%</span>
                <span>25%</span>
                <span>50%</span>
                <span>75%</span>
                <span>100%</span>
              </div>

              {/* Status Badge */}
              {metric.value !== null && (
                <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                  info.label === 'Excellent' || info.label === 'Good' 
                    ? 'bg-emerald-500/10 text-emerald-400' 
                    : 'bg-amber-500/10 text-amber-400'
                }`}>
                  <TrendIcon className="w-3 h-3" />
                  {info.label}
                </div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-6 p-4 bg-dark-800/50 rounded-xl border border-white/5"
      >
        <p className="text-xs text-gray-400 leading-relaxed">
          <span className="text-gold-400 font-medium">💡 Tip:</span> Percentiles show where your contract stands compared to similar roles. 
          Higher salary percentile is better, while lower notice period percentile is generally more favorable.
        </p>
      </motion.div>
    </motion.div>
  )
}

export default PercentileCharts
