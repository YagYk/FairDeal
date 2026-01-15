import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, Shield, BarChart3, MessageSquare, Zap, Check, ArrowRight } from 'lucide-react'
import UploadSection from '../components/UploadSection'
import ProgressSteps from '../components/ProgressSteps'
import AnalysisDashboard from '../components/AnalysisDashboard'
import { AnalysisResult } from '../types'
import { contractAPI } from '../services/api'

const Home = () => {
  const [currentStep, setCurrentStep] = useState<number>(0)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleUpload = async (file: File) => {
    setIsAnalyzing(true)
    setCurrentStep(1)
    setErrorMessage(null)

    try {
      setCurrentStep(1)
      await new Promise(resolve => setTimeout(resolve, 500))

      setCurrentStep(2)
      await new Promise(resolve => setTimeout(resolve, 500))

      setCurrentStep(3)
      const response = await contractAPI.analyze(file)
      
      setCurrentStep(4)
      await new Promise(resolve => setTimeout(resolve, 500))

      setCurrentStep(5)
      await new Promise(resolve => setTimeout(resolve, 500))

      const analysisData = response
      const result: AnalysisResult = {
        fairnessScore: analysisData.fairness_score || 0,
        contractMetadata: {
          contractType: analysisData.contract_metadata?.contract_type || 'unknown',
          industry: analysisData.contract_metadata?.industry || 'unknown',
          role: analysisData.contract_metadata?.role || null,
          location: analysisData.contract_metadata?.location || 'unknown',
          salary: analysisData.contract_metadata?.salary || null,
          noticePeriodDays: analysisData.contract_metadata?.notice_period_days || null,
          nonCompete: analysisData.contract_metadata?.non_compete || false,
        },
        percentileRankings: {
          salary: analysisData.percentile_rankings?.salary || null,
          noticePeriod: analysisData.percentile_rankings?.notice_period || null,
        },
        redFlags: analysisData.red_flags || [],
        favorableTerms: analysisData.favorable_terms || [],
        negotiationPriorities: analysisData.negotiation_priorities || [],
        negotiationScripts: analysisData.negotiation_scripts || [],
        similarContractsCount: analysisData.similar_contracts_count,
        similarContractsDetails: analysisData.similar_contracts_details,
        detailedExplanation: analysisData.detailed_explanation,
      }

      setAnalysisResult(result)
      setAnalysisId(analysisData.analysis_id)
    } catch (error: any) {
      console.error('Analysis error:', error)
      
      if (error.response?.status === 429 || error.rateLimitInfo) {
        const rateLimitInfo = error.rateLimitInfo || {}
        const waitTime = rateLimitInfo.retryAfter || 60
        setErrorMessage(
          `Rate limit exceeded. The API has a limit of 20 requests per minute. Please wait ${waitTime} seconds and try again.`
        )
      } else {
        const errorDetail = error.response?.data?.detail || error.message || 'Unknown error'
        setErrorMessage(`Analysis failed: ${errorDetail}`)
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setCurrentStep(0)
    setAnalysisResult(null)
    setAnalysisId(null)
    setIsAnalyzing(false)
    setErrorMessage(null)
  }

  if (analysisResult) {
    return (
      <div className="min-h-screen py-8">
        <AnalysisDashboard result={analysisResult} analysisId={analysisId || undefined} onReset={handleReset} />
      </div>
    )
  }

  const features = [
    { icon: Shield, title: 'Fairness Score', desc: 'Know if your contract is fair' },
    { icon: BarChart3, title: 'Market Comparison', desc: 'Compare with similar roles' },
    { icon: MessageSquare, title: 'Negotiation Scripts', desc: 'Ready-to-use phrases' },
    { icon: Zap, title: 'Instant Analysis', desc: 'Results in seconds' },
  ]

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-gold-400/5 rounded-full blur-[150px] animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-accent-purple/5 rounded-full blur-[150px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-0 grid-pattern opacity-20" />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-80px)] px-4 sm:px-6 md:px-8 py-12">
        <div className="w-full max-w-3xl mx-auto text-center">
          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-6 leading-[1.1]"
          >
            <span className="text-white">Know your</span>{' '}
            <span className="text-gold-400 italic font-serif">contract's</span>
            <br />
            <span className="text-white">true worth</span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-lg md:text-xl text-gray-400 max-w-xl mb-10 font-light leading-relaxed mx-auto"
          >
            Upload your employment contract and get instant insights on fairness, 
            market comparison, and negotiation strategies.
          </motion.p>

          {/* Error Message */}
          <AnimatePresence>
            {errorMessage && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-8 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start gap-3 text-left max-w-xl mx-auto"
              >
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-red-400 font-medium mb-1">Error</p>
                  <p className="text-gray-300 text-sm">{errorMessage}</p>
                  {errorMessage.includes('Rate limit') && (
                    <p className="text-gray-400 text-xs mt-2">
                      💡 Tip: Wait 1-2 minutes and try again.
                    </p>
                  )}
                  <button
                    onClick={() => setErrorMessage(null)}
                    className="mt-2 text-xs text-red-400 hover:text-red-300 underline"
                  >
                    Dismiss
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Upload / Progress */}
          <AnimatePresence mode="wait">
            {!isAnalyzing ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: 0.3 }}
                className="flex justify-center"
              >
                <UploadSection onUpload={handleUpload} />
              </motion.div>
            ) : (
              <motion.div
                key="progress"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <ProgressSteps currentStep={currentStep} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Trust Badges */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="mt-10 flex flex-wrap items-center justify-center gap-6 text-sm text-gray-500"
          >
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              <span>Private & Secure</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              <span>No Data Stored</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-500" />
              <span>Free to Use</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 py-20 border-t border-white/5">
        <div className="w-full max-w-5xl mx-auto px-4 sm:px-6 md:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl md:text-3xl font-bold mb-3">
              <span className="text-white">What you </span>
              <span className="text-gold-400 italic font-serif">get</span>
            </h2>
            <p className="text-gray-500">Comprehensive contract analysis in seconds</p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="bg-dark-800/30 border border-white/5 rounded-2xl p-5 text-center group hover:border-gold-500/20 transition-all"
              >
                <div className="w-12 h-12 rounded-xl bg-gold-400/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-gold-400/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-gold-400" />
                </div>
                <h3 className="font-semibold text-white mb-1 text-sm md:text-base">{feature.title}</h3>
                <p className="text-xs md:text-sm text-gray-500">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="relative z-10 py-20 border-t border-white/5">
        <div className="w-full max-w-4xl mx-auto px-4 sm:px-6 md:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-12"
          >
            <h2 className="text-2xl md:text-3xl font-bold mb-3">
              <span className="text-white">How it </span>
              <span className="text-gold-400 italic font-serif">works</span>
            </h2>
            <p className="text-gray-500">Three simple steps to contract clarity</p>
          </motion.div>

          <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12">
            {[
              { num: '01', title: 'Upload', desc: 'Drop your contract file' },
              { num: '02', title: 'Analyze', desc: 'AI compares with market data' },
              { num: '03', title: 'Insights', desc: 'Get actionable results' },
            ].map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15 }}
                className="flex flex-col items-center"
              >
                <div className="w-16 h-16 rounded-full bg-gold-400/10 border border-gold-400/20 flex items-center justify-center mb-4">
                  <span className="text-gold-400 font-bold text-lg">{step.num}</span>
                </div>
                <h3 className="text-white font-semibold mb-1">{step.title}</h3>
                <p className="text-gray-500 text-sm">{step.desc}</p>
                {index < 2 && (
                  <ArrowRight className="w-5 h-5 text-gray-600 mt-4 hidden md:block rotate-0 md:rotate-0" />
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home
