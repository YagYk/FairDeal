import { useState, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, X, ArrowRight, Upload, Sparkles } from 'lucide-react'

interface UploadSectionProps {
  onUpload: (file: File) => void
}

const UploadSection = ({ onUpload }: UploadSectionProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    validateAndSetFile(file)
  }

  const validateAndSetFile = (file: File | undefined) => {
    if (!file) return
    
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

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleAnalyze = () => {
    if (selectedFile) {
      onUpload(selectedFile)
    }
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    validateAndSetFile(file)
  }, [])

  return (
    <div className="w-full max-w-xl">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.doc"
        onChange={handleFileSelect}
        className="hidden"
      />

      <AnimatePresence mode="wait">
        {!selectedFile ? (
          <motion.div
            key="upload-zone"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            {/* Drag & Drop Zone */}
            <motion.div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={handleUploadClick}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              className={`relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-300 p-8 text-center ${
                isDragging 
                  ? 'border-gold-400 bg-gold-400/10' 
                  : 'border-white/10 bg-dark-800/30 hover:border-gold-400/50 hover:bg-dark-800/50'
              }`}
            >
              {/* Animated Background */}
              <div className="absolute inset-0 rounded-2xl overflow-hidden pointer-events-none">
                <div className={`absolute inset-0 transition-opacity duration-300 ${isDragging ? 'opacity-100' : 'opacity-0'}`}>
                  <div className="absolute inset-0 bg-gradient-to-r from-gold-400/5 via-transparent to-gold-400/5 animate-gradient-flow" />
                </div>
              </div>

              <div className="relative">
                <motion.div
                  animate={isDragging ? { scale: 1.1, y: -5 } : { scale: 1, y: 0 }}
                  transition={{ type: "spring", stiffness: 300 }}
                  className={`w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center transition-colors ${
                    isDragging ? 'bg-gold-400/20' : 'bg-gold-400/10'
                  }`}
                >
                  <Upload className={`w-8 h-8 transition-colors ${isDragging ? 'text-gold-400' : 'text-gold-500'}`} />
                </motion.div>

                <h3 className="text-lg font-semibold text-white mb-2">
                  {isDragging ? 'Drop your contract here' : 'Upload your contract'}
                </h3>
                <p className="text-sm text-gray-400 mb-4">
                  Drag and drop or click to browse
                </p>
                <p className="text-xs text-gray-500">
                  Supports PDF, DOC, DOCX (Max 10MB)
                </p>
              </div>
            </motion.div>

            {/* OR Divider */}
            <div className="flex items-center gap-4 my-6">
              <div className="flex-1 h-px bg-white/10" />
              <span className="text-gray-500 text-sm">or</span>
              <div className="flex-1 h-px bg-white/10" />
            </div>

            {/* Upload Button */}
            <motion.button
              onClick={handleUploadClick}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full inline-flex items-center justify-center gap-3 bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 font-bold px-8 py-4 rounded-full uppercase tracking-wider text-sm shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all"
            >
              <Sparkles className="w-5 h-5" />
              <span>Select Contract File</span>
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            key="file-selected"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="space-y-4"
          >
            {/* Selected File Card */}
            <div className="liquid-glass rounded-2xl p-4 flex items-center justify-between gap-3 gradient-border">
              <div className="flex items-center gap-4 min-w-0 flex-1">
                <motion.div
                  initial={{ rotate: -10 }}
                  animate={{ rotate: 0 }}
                  className="w-14 h-14 rounded-xl bg-gradient-to-br from-gold-400/20 to-amber-500/10 flex items-center justify-center flex-shrink-0"
                >
                  <FileText className="w-7 h-7 text-gold-400" />
                </motion.div>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-white truncate">{selectedFile.name}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-sm text-gray-400">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                    <span className="w-1 h-1 rounded-full bg-gray-600" />
                    <span className="text-sm text-emerald-400">Ready to analyze</span>
                  </div>
                </div>
              </div>
              <motion.button
                onClick={handleRemoveFile}
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                className="p-2.5 rounded-xl bg-white/5 hover:bg-red-500/10 transition-colors cursor-pointer group"
              >
                <X className="w-5 h-5 text-gray-400 group-hover:text-red-400 transition-colors" />
              </motion.button>
            </div>

            {/* Analyze Button */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleAnalyze}
              className="w-full inline-flex items-center justify-center gap-3 bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 font-bold px-8 py-4 rounded-full uppercase tracking-wider text-sm shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all"
            >
              <Sparkles className="w-5 h-5" />
              <span>Analyze Contract</span>
              <ArrowRight className="w-5 h-5" />
            </motion.button>

            {/* Change File Link */}
            <button
              onClick={handleUploadClick}
              className="w-full text-center text-sm text-gray-400 hover:text-gold-400 transition-colors"
            >
              Choose a different file
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default UploadSection
