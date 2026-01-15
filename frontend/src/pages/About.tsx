import { motion } from 'framer-motion'
import { Shield, Users, Trophy, Target, Heart, Sparkles, ArrowRight, Zap, Eye, Lock } from 'lucide-react'
import { Link } from 'react-router-dom'

const About = () => {
  const values = [
    {
      icon: Shield,
      title: "Protection First",
      desc: "We analyze contracts to identify clauses that put you at a disadvantage.",
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
    },
    {
      icon: Trophy,
      title: "Market Standards",
      desc: "Compare your offer against industry benchmarks to ensure you're getting what you're worth.",
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
    },
    {
      icon: Users,
      title: "Expert Insights",
      desc: "Get negotiation scripts and strategies crafted by legal and HR experts.",
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
    },
  ]

  const principles = [
    {
      icon: Eye,
      title: "Transparency",
      desc: "Every insight is backed by real data. We show you exactly how we reached our conclusions.",
    },
    {
      icon: Lock,
      title: "Privacy",
      desc: "Your contracts are processed securely and never stored permanently. Your data is yours.",
    },
    {
      icon: Zap,
      title: "Speed",
      desc: "Get comprehensive analysis in seconds, not days. Make informed decisions faster.",
    },
    {
      icon: Target,
      title: "Accuracy",
      desc: "AI-powered analysis trained on real Indian employment contracts for precise insights.",
    },
  ]

  const stats = [
    { number: '10K+', label: 'Contracts Analyzed' },
    { number: '95%', label: 'User Satisfaction' },
    { number: '50+', label: 'Data Points Checked' },
    { number: '24/7', label: 'Availability' },
  ]

  return (
    <div className="w-full relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-gold-400/5 rounded-full blur-[150px]" />
        <div className="absolute bottom-1/4 left-1/4 w-[500px] h-[500px] bg-accent-purple/5 rounded-full blur-[150px]" />
        <div className="absolute inset-0 grid-pattern opacity-30" />
      </div>

      {/* Hero Section */}
      <section className="relative z-10 max-w-6xl mx-auto pt-32 pb-20 px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold-400/10 border border-gold-400/20 mb-6"
          >
            <Heart className="w-4 h-4 text-gold-400" />
            <span className="text-sm text-gold-300 font-medium">Our Mission</span>
          </motion.div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="text-white">Democratizing</span>{' '}
            <span className="text-gold-400 italic font-serif">Fairness</span>
          </h1>
          
          <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
            We believe every professional deserves a fair deal. Our AI-driven platform
            levels the playing field in employment negotiations.
          </p>
        </motion.div>

        {/* Values Grid */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20"
        >
          {values.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              whileHover={{ y: -5, scale: 1.02 }}
              className="liquid-glass rounded-2xl p-8 text-center group gradient-border"
            >
              <div className={`w-16 h-16 ${item.bgColor} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform`}>
                <item.icon className={`w-8 h-8 ${item.color}`} />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-white">{item.title}</h3>
              <p className="text-gray-400 leading-relaxed">{item.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 py-20 border-y border-white/5">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl md:text-5xl font-bold text-gold-400 mb-2">{stat.number}</div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Principles Section */}
      <section className="relative z-10 max-w-6xl mx-auto py-20 px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="text-white">Our</span>{' '}
            <span className="text-gold-400 italic font-serif">Principles</span>
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            The values that guide everything we build
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {principles.map((item, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="liquid-glass rounded-2xl p-6 flex items-start gap-4 group hover:bg-white/5 transition-colors"
            >
              <div className="w-12 h-12 rounded-xl bg-gold-500/10 flex items-center justify-center flex-shrink-0 group-hover:bg-gold-500/20 transition-colors">
                <item.icon className="w-6 h-6 text-gold-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400 leading-relaxed">{item.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 max-w-4xl mx-auto px-6 pb-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="liquid-glass rounded-3xl p-10 md:p-16 text-center gradient-border"
        >
          <Sparkles className="w-16 h-16 text-gold-400 mx-auto mb-6" />
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <span className="text-white">Ready to analyze</span>{' '}
            <span className="text-gold-400 italic font-serif">your contract?</span>
          </h2>
          <p className="text-gray-400 mb-8 max-w-xl mx-auto">
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
        </motion.div>
      </section>
    </div>
  )
}

export default About
