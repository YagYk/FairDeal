import { motion } from 'framer-motion'
import { BarChart as BarChartIcon } from 'lucide-react'
import { PercentileRankings } from '../types'

interface PercentileChartsProps {
  rankings: PercentileRankings
}

const PercentileCharts = ({ rankings }: PercentileChartsProps) => {
  const data = [
    {
      name: 'Salary',
      value: rankings.salary,
      color: rankings.salary !== null && rankings.salary >= 70 ? '#10b981' : rankings.salary !== null && rankings.salary >= 40 ? '#f59e0b' : '#6b7280',
      hasValue: rankings.salary !== null,
    },
    {
      name: 'Notice Period',
      value: rankings.noticePeriod,
      color: rankings.noticePeriod !== null && rankings.noticePeriod <= 30 ? '#10b981' : rankings.noticePeriod !== null && rankings.noticePeriod <= 60 ? '#f59e0b' : '#6b7280',
      hasValue: rankings.noticePeriod !== null,
    },
  ].filter(item => item.hasValue) // Only show items with values

  const getLabel = (value: number | null, name: string) => {
    if (value === null) return 'Not available'
    if (name === 'Notice Period') {
      // Lower is better for notice period
      if (value <= 30) return 'Excellent'
      if (value <= 60) return 'Good'
      return 'Above Average'
    } else {
      // Higher is better for salary
      if (value >= 70) return 'Excellent'
      if (value >= 40) return 'Good'
      return 'Below Average'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-effect rounded-2xl p-6"
    >
      <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
        <BarChartIcon className="w-5 h-5 text-gold-500" />
        Market Percentile Rankings
      </h3>
      
      <div className="space-y-6">
        {data.length > 0 ? (
          data.map((item, index) => (
            <div key={item.name}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium">{item.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold" style={{ color: item.color }}>
                    {item.value !== null ? `${item.value}%` : 'N/A'}
                  </span>
                  <span className="text-xs text-gray-400">percentile</span>
                </div>
              </div>
              {item.value !== null && (
                <>
                  <div className="relative h-8 bg-dark-700 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.value}%` }}
                      transition={{ delay: index * 0.2, duration: 1 }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">
                    {getLabel(item.value, item.name)} compared to market
                  </p>
                </>
              )}
            </div>
          ))
        ) : (
          <p className="text-gray-400 text-sm">No percentile data available. This may be because there are no similar contracts in the knowledge base yet.</p>
        )}
      </div>

      <div className="mt-6 pt-6 border-t border-dark-600">
        <p className="text-xs text-gray-400">
          Percentile indicates where your contract terms rank compared to similar contracts. 
          Higher is better for salary, lower is better for notice period.
        </p>
      </div>
    </motion.div>
  )
}

export default PercentileCharts

