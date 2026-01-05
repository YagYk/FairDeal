import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  Shield,
  FileText,
  MessageSquare,
  BarChart3,
  Zap,
  Lock,
  Globe,
  Target,
  CheckCircle2,
  Eye,
  ArrowRight,
  Sparkles
} from 'lucide-react'

const Features = () => {
  const features = [
    {
      icon: Shield,
      title: 'Fairness Analysis',
      description: 'Comprehensive fairness score (0-100) evaluating your contract against industry standards.',
      gradient: 'from-blue-500/20 to-cyan-500/20',
      iconColor: 'text-blue-400',
    },
    {
      icon: BarChart3,
      title: 'Percentile Rankings',
      description: 'See where your salary, notice period, and terms rank compared to similar contracts.',
      gradient: 'from-green-500/20 to-emerald-500/20',
      iconColor: 'text-green-400',
    },
    {
      icon: FileText,
      title: 'Clause Detection',
      description: 'AI identifies and explains every important clause in your contract automatically.',
      gradient: 'from-purple-500/20 to-pink-500/20',
      iconColor: 'text-purple-400',
    },
    {
      icon: MessageSquare,
      title: 'Negotiation Scripts',
      description: 'Ready-to-use, professional scripts tailored to your specific contract terms.',
      gradient: 'from-amber-500/20 to-orange-500/20',
      iconColor: 'text-amber-400',
    },
    {
      icon: Zap,
      title: 'Instant Analysis',
      description: 'Get comprehensive insights in seconds, not hours or days.',
      gradient: 'from-yellow-500/20 to-gold-400/20',
      iconColor: 'text-yellow-400',
    },
    {
      icon: Lock,
      title: 'Privacy First',
      description: 'Your contracts are processed securely and never stored permanently.',
      gradient: 'from-red-500/20 to-rose-500/20',
      iconColor: 'text-red-400',
    },
    {
      icon: Globe,
      title: 'India-Focused',
      description: 'Trained on Indian employment contracts with local market context.',
      gradient: 'from-indigo-500/20 to-blue-500/20',
      iconColor: 'text-indigo-400',
    },
    {
      icon: Target,
      title: 'Actionable Insights',
      description: 'Know exactly what to negotiate and what success probability to expect.',
      gradient: 'from-teal-500/20 to-cyan-500/20',
      iconColor: 'text-teal-400',
    },
  ]

  const highlights = [
    {
      stat: '50%',
      label: 'Faster than manual review',
      color: 'text-purple-400',
    },
    {
      stat: '20+',
      label: 'Similar contracts compared',
      color: 'text-blue-400',
    },
    {
      stat: '100%',
      label: 'Privacy protected',
      color: 'text-green-400',
    },
  ]

  return (
    <div className="w-full">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center px-8 py-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-6xl mx-auto text-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-7xl md:text-8xl font-bold mb-8"
          >
            <span className="text-white">Powerful</span>
            <br />
            <span className="text-gold-400 italic font-serif">Features</span>
          </motion.div>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto font-light"
          >
            Everything you need to understand, compare, and negotiate your contract with confidence.
          </motion.p>
        </motion.div>
      </section>

      {/* Features Grid - Apple Keynote Style */}
      <section className="px-8 py-24">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-50px' }}
                  transition={{ delay: index * 0.1, duration: 0.6 }}
                  whileHover={{ scale: 1.02, y: -5 }}
                  className="liquid-glass rounded-2xl p-6 group cursor-pointer"
                >
                  <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className={`w-7 h-7 ${feature.iconColor}`} />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-400 leading-relaxed">{feature.description}</p>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Performance Stats - Apple Style */}
      <section className="px-8 py-24">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <div className="text-5xl md:text-6xl font-bold mb-4">
              <span className="text-white">Designed for</span>
              <br />
              <span className="text-gold-400 italic font-serif">speed and accuracy.</span>
            </div>
          </motion.div>
          <div className="grid md:grid-cols-3 gap-8">
            {highlights.map((highlight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                className="liquid-glass rounded-2xl p-8 text-center"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.2 + 0.3, type: 'spring', stiffness: 200 }}
                  className={`text-6xl font-bold mb-2 ${highlight.color}`}
                >
                  {highlight.stat}
                </motion.div>
                <p className="text-gray-400 text-sm">{highlight.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Differentiators */}
      <section className="px-8 py-24">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-100px' }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <div className="text-5xl md:text-6xl font-bold mb-4">
              <span className="text-white">Why this is</span>
              <br />
              <span className="text-gold-400 italic font-serif">different.</span>
            </div>
          </motion.div>
          <div className="grid md:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="liquid-glass rounded-2xl p-8"
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gold-500/20 to-amber-500/20 flex items-center justify-center flex-shrink-0">
                  <CheckCircle2 className="w-6 h-6 text-gold-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-2">Real Data, Not Opinions</h3>
                  <p className="text-gray-400 leading-relaxed">
                    Every insight is backed by actual contracts from the market. No generic advice.
                  </p>
                </div>
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8 }}
              className="liquid-glass rounded-2xl p-8"
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center flex-shrink-0">
                  <Eye className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-2">Full Transparency</h3>
                  <p className="text-gray-400 leading-relaxed">
                    See exactly which contracts we compared against. Understand every recommendation.
                  </p>
                </div>
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="liquid-glass rounded-2xl p-8"
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center flex-shrink-0">
                  <Target className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-2">Actionable, Not Abstract</h3>
                  <p className="text-gray-400 leading-relaxed">
                    Get specific negotiation scripts with success probabilities. Know what to say and when.
                  </p>
                </div>
              </div>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: '-100px' }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="liquid-glass rounded-2xl p-8"
            >
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <Lock className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white mb-2">Privacy by Design</h3>
                  <p className="text-gray-400 leading-relaxed">
                    Your contract is analyzed and deleted. We never store your personal documents.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-8 py-24">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-100px' }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center"
        >
          <div className="liquid-glass rounded-3xl p-12 md:p-16">
            <Sparkles className="w-16 h-16 text-gold-400 mx-auto mb-6" />
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="text-white">Ready to analyze</span>
              <br />
              <span className="text-gold-400 italic font-serif">your contract?</span>
            </h2>
            <p className="text-xl text-gray-300 mb-8 font-light max-w-2xl mx-auto">
              Get instant insights into fairness, market position, and negotiation opportunities.
            </p>
            <Link to="/">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="inline-flex items-center gap-3 bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 font-bold px-8 py-4 rounded-full uppercase tracking-wider text-sm shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all"
              >
                <span>Get Started</span>
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  )
}

export default Features
