import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { FileText, X, ArrowRight } from 'lucide-react'

interface UploadSectionProps {
  onUpload: (file: File) => void
}

const UploadSection = ({ onUpload }: UploadSectionProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        alert('File size must be less than 10MB')
        return
      }
      if (!file.type.includes('pdf') && !file.name.endsWith('.docx') && !file.name.endsWith('.doc')) {
        alert('Please upload a PDF or DOCX file')
        return
      }
      setSelectedFile(file)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
  }

  const handleAnalyze = () => {
    if (selectedFile) {
      onUpload(selectedFile)
    }
  }

  return (
    <div className="w-full max-w-2xl">
      {!selectedFile ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            onChange={handleFileSelect}
            className="hidden"
          />
          <motion.button
            onClick={handleUploadClick}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="inline-flex items-center gap-2 sm:gap-3 bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 font-bold px-6 sm:px-8 py-3 sm:py-4 rounded-full uppercase tracking-wider text-xs sm:text-sm shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all cursor-pointer w-full sm:w-auto justify-center"
          >
            <span>UPLOAD CONTRACT</span>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-dark-900 rounded-full"></div>
              <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
          </motion.button>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-4"
        >
          <div className="liquid-glass rounded-2xl p-3 sm:p-4 flex items-center justify-between gap-2">
            <div className="flex items-center gap-3 sm:gap-4 min-w-0 flex-1">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-gold-400/20 to-amber-500/20 flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 sm:w-6 sm:h-6 text-gold-400" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-white text-sm sm:text-base truncate">{selectedFile.name}</p>
                <p className="text-xs sm:text-sm text-gray-400">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <motion.button
              onClick={handleRemoveFile}
              whileHover={{ scale: 1.1, rotate: 90 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5 text-gray-400" />
            </motion.button>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleAnalyze}
            className="w-full inline-flex items-center justify-center gap-2 sm:gap-3 bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 font-bold px-6 sm:px-8 py-3 sm:py-4 rounded-full uppercase tracking-wider text-xs sm:text-sm shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all"
          >
            <span>ANALYZE CONTRACT</span>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-dark-900 rounded-full"></div>
              <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
          </motion.button>
        </motion.div>
      )}
    </div>
  )
}

export default UploadSection
