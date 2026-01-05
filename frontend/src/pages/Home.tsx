import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
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

    try {
      // Step 1: Uploading
      setCurrentStep(1)
      await new Promise(resolve => setTimeout(resolve, 500))

      // Step 2: Extracting text
      setCurrentStep(2)
      await new Promise(resolve => setTimeout(resolve, 500))

      // Step 3: Analyzing contract
      setCurrentStep(3)
      const response = await contractAPI.analyze(file)
      
      // Step 4: Computing statistics
      setCurrentStep(4)
      await new Promise(resolve => setTimeout(resolve, 500))

      // Step 5: Generating insights
      setCurrentStep(5)
      await new Promise(resolve => setTimeout(resolve, 500))

      // Transform API response to frontend format
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
      setAnalysisId(analysisData.analysis_id) // Store analysis ID for chatbot
    } catch (error: any) {
      console.error('Analysis error:', error)
      
      // Check for rate limit error
      if (error.response?.status === 429 || error.rateLimitInfo) {
        const rateLimitInfo = error.rateLimitInfo || {}
        const waitTime = rateLimitInfo.retryAfter || 60
        setErrorMessage(
          `Rate limit exceeded. The API has a limit of 20 requests per minute. Please wait ${waitTime} seconds and try again.`
        )
      } else {
        // Regular error
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
      <div className="min-h-screen pt-24 pb-24">
        <AnalysisDashboard result={analysisResult} analysisId={analysisId || undefined} onReset={handleReset} />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col pb-32 md:pb-24 pt-20 md:pt-24">
      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 md:px-8 pt-8 pb-8">
        <div className="w-full max-w-5xl mx-auto">
          {/* Small uppercase text above headline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xs sm:text-sm uppercase tracking-[0.3em] text-gray-400 mb-6 md:mb-8 font-sans text-center md:text-left"
          >
            CONTRACT ANALYSIS PLATFORM
          </motion.p>

          {/* Large Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold mb-6 md:mb-8 leading-[1.1] text-center md:text-left"
          >
            <span className="text-white font-sans">We analyze</span>{' '}
            <span className="text-gold-400 italic font-serif">contracts</span>{' '}
            <span className="text-white font-sans">fairly</span>
          </motion.h1>

          {/* Descriptive paragraph */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-base sm:text-lg md:text-xl text-gray-300 max-w-2xl mb-8 md:mb-12 font-light leading-relaxed text-center md:text-left mx-auto md:mx-0"
          >
            AI-powered contract analysis platform that helps you understand contract terms,
            compare with market standards, and get negotiation insights for Indian professionals.
          </motion.p>

          {/* Error Message */}
          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-red-400 font-medium mb-1">Error</p>
                <p className="text-gray-300 text-sm">{errorMessage}</p>
                {errorMessage.includes('Rate limit') && (
                  <p className="text-gray-400 text-xs mt-2">
                    💡 Tip: Wait 1-2 minutes and try again. The free tier allows 20 requests per minute.
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

          {/* CTA Button */}
          <AnimatePresence mode="wait">
            {!isAnalyzing ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: 0.4 }}
                className="flex justify-center md:justify-start"
              >
                <UploadSection onUpload={handleUpload} />
              </motion.div>
            ) : (
              <motion.div
                key="progress"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex justify-center md:justify-start"
              >
                <ProgressSteps currentStep={currentStep} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

    </div>
  )
}

export default Home
