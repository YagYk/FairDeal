import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { User, Mail, LogOut, FileText, BarChart3, Settings } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { profileAPI } from '../services/api'

interface Stats {
  total_analyses: number
  average_score: number
  account_status: string
}

interface Analysis {
  id: string
  contract_filename: string
  fairness_score: number
  contract_type: string | null
  industry: string | null
  role: string | null
  created_at: string | null
}

const Profile = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState<Stats | null>(null)
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        setIsLoading(true)
        const [statsData, analysesData] = await Promise.all([
          profileAPI.getStats(),
          profileAPI.getAnalyses(10),
        ])
        setStats(statsData)
        setAnalyses(analysesData)
      } catch (error) {
        console.error('Error fetching profile data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchProfileData()
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const statItems = stats ? [
    { icon: FileText, label: 'Contracts Analyzed', value: stats.total_analyses.toString(), color: 'text-blue-400' },
    { icon: BarChart3, label: 'Average Score', value: stats.average_score.toString(), color: 'text-green-400' },
    { icon: Settings, label: 'Account Status', value: stats.account_status, color: 'text-gold-400' },
  ] : []

  return (
    <div className="min-h-screen pt-24 pb-24 px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <div className="text-5xl md:text-6xl font-bold mb-4">
            <span className="text-white">Profile</span>
          </div>
          <p className="text-xl text-gray-300 font-light">Manage your account and view your analysis history</p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Profile Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1, duration: 0.6 }}
            className="liquid-glass rounded-2xl p-8"
          >
            <div className="text-center mb-6">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-gold-400 via-gold-500 to-amber-600 flex items-center justify-center mx-auto mb-4">
                <User className="w-12 h-12 text-dark-900" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">{user?.name || 'User'}</h2>
              <div className="flex items-center justify-center gap-2 text-gray-400">
                <Mail className="w-4 h-4" />
                <span className="text-sm">{user?.email}</span>
              </div>
            </div>
            <motion.button
              onClick={handleLogout}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-all"
            >
              <LogOut className="w-5 h-5" />
              <span>Sign Out</span>
            </motion.button>
          </motion.div>

          {/* Stats Grid */}
          <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-6">
            {isLoading ? (
              <div className="col-span-3 flex items-center justify-center py-12">
                <div className="w-8 h-8 border-2 border-gold-400 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : (
              statItems.map((stat, index) => {
              const Icon = stat.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 + index * 0.1, duration: 0.6 }}
                  className="liquid-glass rounded-2xl p-6"
                >
                  <Icon className={`w-8 h-8 ${stat.color} mb-4`} />
                  <div className={`text-3xl font-bold ${stat.color} mb-2`}>{stat.value}</div>
                  <p className="text-sm text-gray-400">{stat.label}</p>
                </motion.div>
              )
            }))}
          </div>
        </div>

        {/* Analysis History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="mt-8"
        >
          <div className="liquid-glass rounded-2xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">Recent Analyses</h3>
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <div className="w-8 h-8 border-2 border-gold-400 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : analyses.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No analyses yet. Upload your first contract to get started!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {analyses.map((analysis, index) => (
                  <motion.div
                    key={analysis.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                    className="flex items-center justify-between p-4 rounded-xl bg-dark-800/50 border border-white/5 hover:bg-dark-800/70 transition-all"
                  >
                    <div className="flex items-center gap-4">
                      <FileText className="w-8 h-8 text-gold-400" />
                      <div>
                        <p className="text-white font-medium">{analysis.contract_filename}</p>
                        <p className="text-sm text-gray-400">
                          {analysis.created_at
                            ? new Date(analysis.created_at).toLocaleDateString()
                            : 'Date not available'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-gold-400 font-bold text-lg">{analysis.fairness_score}%</div>
                      <div className="text-xs text-gray-400">Fairness Score</div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Profile

