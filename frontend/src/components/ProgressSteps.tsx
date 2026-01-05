import { motion } from 'framer-motion'
import { Check, Loader2 } from 'lucide-react'

interface ProgressStepsProps {
  currentStep: number
}

const steps = [
  { label: 'Uploading', description: 'Processing your contract file' },
  { label: 'Extracting', description: 'Analyzing contract structure' },
  { label: 'Comparing', description: 'Finding similar contracts' },
  { label: 'Analyzing', description: 'Computing fairness metrics' },
  { label: 'Generating', description: 'Creating insights & scripts' },
]

const ProgressSteps = ({ currentStep }: ProgressStepsProps) => {
  return (
    <div className="max-w-3xl mx-auto glass-effect rounded-2xl p-8 md:p-12">
      <h2 className="text-2xl font-semibold mb-8 text-center">
        Analyzing Your Contract
      </h2>

      <div className="space-y-6">
        {steps.map((step, index) => {
          const stepNumber = index + 1
          const isCompleted = stepNumber < currentStep
          const isActive = stepNumber === currentStep

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center gap-4"
            >
              <div className="flex-shrink-0">
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-12 h-12 rounded-full bg-gold-500 flex items-center justify-center"
                  >
                    <Check className="w-6 h-6 text-white" />
                  </motion.div>
                ) : isActive ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-12 h-12 rounded-full border-4 border-gold-500 border-t-transparent flex items-center justify-center"
                  >
                    <Loader2 className="w-6 h-6 text-gold-500" />
                  </motion.div>
                ) : (
                  <div className="w-12 h-12 rounded-full border-2 border-dark-600 flex items-center justify-center">
                    <span className="text-gray-500">{stepNumber}</span>
                  </div>
                )}
              </div>

              <div className="flex-1">
                <h3
                  className={`font-semibold ${isActive ? 'text-gold-500' : isCompleted ? 'text-white' : 'text-gray-500'
                    }`}
                >
                  {step.label}
                </h3>
                <p className="text-sm text-gray-400">{step.description}</p>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

export default ProgressSteps

