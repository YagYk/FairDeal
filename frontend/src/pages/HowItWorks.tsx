import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import { FileText, Sparkles, AlertTriangle, CheckCircle2, MessageSquare, Eye, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

const HowItWorks = () => {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end']
  })

  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0])
  const y = useTransform(scrollYProgress, [0, 0.2], [0, -50])

  return (
    <div ref={containerRef} className="w-full">
      {/* Section 1: The Problem */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <motion.div
          style={{ opacity, y }}
          className="max-w-4xl mx-auto text-center"
        >
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-5xl md:text-7xl font-bold mb-8 leading-tight"
          >
            <span className="text-white">Reading a contract</span>
            <br />
            <span className="text-gold-400 italic font-serif">doesn't tell you</span>
            <br />
            <span className="text-white">if it's fair.</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto font-light leading-relaxed"
          >
            A clause means nothing without context. We give you that context.
          </motion.p>
        </motion.div>
      </section>

      {/* Section 2: Upload */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <div className="max-w-6xl mx-auto w-full">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
            >
              <div className="text-5xl md:text-6xl font-bold mb-6">
                <span className="text-white">Drop in</span>
                <br />
                <span className="text-gold-400 italic font-serif">your contract.</span>
              </div>
              <p className="text-xl text-gray-300 font-light leading-relaxed">
                PDF or DOCX. No formatting needed. No legal knowledge required.
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="liquid-glass rounded-2xl p-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-gold-500/10 to-transparent" />
                <FileText className="w-16 h-16 text-gold-400 mx-auto mb-4" />
                <div className="text-center">
                  <p className="text-white font-semibold mb-2">contract.pdf</p>
                  <p className="text-sm text-gray-400">2.4 MB</p>
                </div>
                <motion.div
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  className="absolute top-4 right-4 w-3 h-3 bg-gold-400 rounded-full"
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ repeat: Infinity, duration: 2 }}
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Section 3: Understanding */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <div className="max-w-6xl mx-auto w-full">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="relative"
            >
              <div className="liquid-glass rounded-2xl p-8 space-y-4">
                <div className="space-y-3">
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                    className="flex items-center gap-3"
                  >
                    <Sparkles className="w-5 h-5 text-gold-400" />
                    <span className="text-white">Notice Period: 90 days</span>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 }}
                    className="flex items-center gap-3"
                  >
                    <Sparkles className="w-5 h-5 text-gold-400" />
                    <span className="text-white">Salary: ₹15,00,000</span>
                  </motion.div>
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 }}
                    className="flex items-center gap-3"
                  >
                    <Sparkles className="w-5 h-5 text-gold-400" />
                    <span className="text-white">Non-compete: Yes</span>
                  </motion.div>
                </div>
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
            >
              <div className="text-5xl md:text-6xl font-bold mb-6">
                <span className="text-white">We don't just</span>
                <br />
                <span className="text-gold-400 italic font-serif">read it.</span>
                <br />
                <span className="text-white">We understand it.</span>
              </div>
              <p className="text-xl text-gray-300 font-light leading-relaxed">
                We identify what matters. Salary. Notice period. Clauses. Context, not keywords.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Section 4: Comparison */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <div className="max-w-6xl mx-auto w-full text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.8 }}
            className="mb-16"
          >
            <div className="text-5xl md:text-6xl font-bold mb-6">
              <span className="text-white">Your contract,</span>
              <br />
              <span className="text-gold-400 italic font-serif">placed inside</span>
              <br />
              <span className="text-white">the real market.</span>
            </div>
            <p className="text-xl text-gray-300 font-light max-w-2xl mx-auto">
              We find similar contracts. Same role. Same industry. Real data, not opinions.
            </p>
          </motion.div>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            {[1, 2, 3, 4, 5].map((i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: i === 3 ? 1 : 0.3, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                className={`liquid-glass rounded-xl p-4 w-24 h-32 flex items-center justify-center ${
                  i === 3 ? 'ring-2 ring-gold-400' : ''
                }`}
              >
                <FileText className={`w-8 h-8 ${i === 3 ? 'text-gold-400' : 'text-gray-500'}`} />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Section 5: Statistics */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <div className="max-w-6xl mx-auto w-full">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
            >
              <div className="text-5xl md:text-6xl font-bold mb-6">
                <span className="text-white">Fairness isn't</span>
                <br />
                <span className="text-gold-400 italic font-serif">a feeling.</span>
                <br />
                <span className="text-white">It's a percentile.</span>
              </div>
              <p className="text-xl text-gray-300 font-light leading-relaxed">
                Your notice period is longer than 87% of similar contracts. That's data, not guesswork.
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="liquid-glass rounded-2xl p-8"
            >
              <div className="mb-6">
                <div className="flex justify-between mb-2">
                  <span className="text-white">Notice Period</span>
                  <span className="text-gold-400 font-semibold">87th percentile</span>
                </div>
                <div className="h-3 bg-dark-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: '87%' }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: 0.3 }}
                    className="h-full bg-gradient-to-r from-gold-500 to-amber-500 rounded-full"
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-white">Salary</span>
                  <span className="text-gold-400 font-semibold">65th percentile</span>
                </div>
                <div className="h-3 bg-dark-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: '65%' }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: 0.5 }}
                    className="h-full bg-gradient-to-r from-gold-500 to-amber-500 rounded-full"
                  />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Section 6: Insights */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <div className="max-w-6xl mx-auto w-full">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <div className="text-5xl md:text-6xl font-bold mb-6">
              <span className="text-white">Not advice.</span>
              <br />
              <span className="text-gold-400 italic font-serif">Intelligence.</span>
            </div>
            <p className="text-xl text-gray-300 font-light max-w-2xl mx-auto">
              Red flags. Favorable terms. What matters. What to negotiate first.
            </p>
          </motion.div>
          <div className="grid md:grid-cols-2 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="liquid-glass rounded-2xl p-6 group hover:bg-white/5 transition-all"
            >
              <AlertTriangle className="w-8 h-8 text-red-400 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">90-day notice period</h3>
              <p className="text-gray-400 text-sm">Above market average. Consider negotiating to 60 days.</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="liquid-glass rounded-2xl p-6 group hover:bg-white/5 transition-all"
            >
              <CheckCircle2 className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Competitive salary</h3>
              <p className="text-gray-400 text-sm">In the 65th percentile. This is good.</p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Section 7: Negotiation */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <div className="max-w-6xl mx-auto w-full">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
            >
              <div className="text-5xl md:text-6xl font-bold mb-6">
                <span className="text-white">Know what</span>
                <br />
                <span className="text-gold-400 italic font-serif">to say —</span>
                <br />
                <span className="text-white">and why.</span>
              </div>
              <p className="text-xl text-gray-300 font-light leading-relaxed">
                We generate scripts. Grounded in data. Clear. Professional. Non-aggressive.
              </p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="liquid-glass rounded-2xl p-8"
            >
              <MessageSquare className="w-8 h-8 text-gold-400 mb-4" />
              <p className="text-white font-light leading-relaxed mb-4">
                "I'd like to discuss the notice period. A 90-day period is above industry standard. Would it be possible to reduce this to 60 days?"
              </p>
              <div className="flex items-center gap-2 mt-4">
                <div className="flex-1 h-2 bg-dark-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: '70%' }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: 0.5 }}
                    className="h-full bg-gold-400 rounded-full"
                  />
                </div>
                <span className="text-sm text-gray-400">70% success</span>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Section 8: Trust & Transparency */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <div className="max-w-6xl mx-auto w-full text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.8 }}
            className="mb-16"
          >
            <div className="text-5xl md:text-6xl font-bold mb-6">
              <span className="text-white">You always know</span>
              <br />
              <span className="text-gold-400 italic font-serif">why we said</span>
              <br />
              <span className="text-white">what we said.</span>
            </div>
            <p className="text-xl text-gray-300 font-light max-w-2xl mx-auto">
              See similar contracts used. Understand reasoning. No black-box answers.
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="liquid-glass rounded-2xl p-8 max-w-2xl mx-auto"
          >
            <Eye className="w-12 h-12 text-gold-400 mx-auto mb-6" />
            <button className="px-6 py-3 rounded-full bg-white/5 hover:bg-white/10 text-white font-medium transition-all">
              Why?
            </button>
            <p className="text-gray-400 text-sm mt-4">
              Click to see the 20 similar contracts we compared against
            </p>
          </motion.div>
        </div>
      </section>

      {/* Section 9: Final Summary */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <div className="text-5xl md:text-6xl font-bold mb-12">
            <span className="text-white">From uncertainty</span>
            <br />
            <span className="text-gold-400 italic font-serif">to clarity —</span>
            <br />
            <span className="text-white">before you sign.</span>
          </div>
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
            >
              <div className="text-3xl font-bold text-gold-400 mb-2">Context</div>
              <p className="text-gray-400">Real market data, not assumptions.</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
            >
              <div className="text-3xl font-bold text-gold-400 mb-2">Comparison</div>
              <p className="text-gray-400">Your contract against similar ones.</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              <div className="text-3xl font-bold text-gold-400 mb-2">Confidence</div>
              <p className="text-gray-400">Know what to negotiate and how.</p>
            </motion.div>
          </div>
          <Link to="/">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-3 bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 font-bold px-8 py-4 rounded-full uppercase tracking-wider text-sm shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all"
            >
              <span>Upload your contract</span>
              <ArrowRight className="w-5 h-5" />
            </motion.button>
          </Link>
        </motion.div>
      </section>
    </div>
  )
}

export default HowItWorks
