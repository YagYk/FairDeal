import { motion } from 'framer-motion'
import { Shield, Users, Trophy } from 'lucide-react'

const About = () => {
  return (
    <div className="w-full max-w-6xl mx-auto pt-24 pb-24 px-8">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto mb-20">
        <motion.p
          className="text-xs uppercase tracking-[0.3em] text-gray-400 mb-4 font-sans"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          ABOUT
        </motion.p>
        <motion.h1
          className="text-6xl md:text-7xl font-bold mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <span className="text-white font-sans">Democratizing</span>{' '}
          <span className="text-gold-400 italic font-serif">Fairness</span>
        </motion.h1>
        <motion.p
          className="text-xl text-gray-300 relative z-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          We believe every professional deserves a fair deal. Our AI-driven platform
          levels the playing field in employment negotiations.
        </motion.p>
      </div>

      <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
        {[
          {
            icon: Shield,
            title: "Protection First",
            desc: "We analyze contracts to identify clauses that put you at a disadvantage."
          },
          {
            icon: Trophy,
            title: "Market Standards",
            desc: "Compare your offer against industry benchmarks to ensure you're getting what you're worth."
          },
          {
            icon: Users,
            title: "Expert Insights",
            desc: "Get negotiation scripts and strategies crafted by legal and HR experts."
          }
        ].map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + (index * 0.1) }}
            className="glass-card p-8 text-center"
          >
            <div className="w-16 h-16 bg-gold-500/10 rounded-2xl flex items-center justify-center mx-auto mb-6 text-gold-500">
              <item.icon className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-4 text-white">{item.title}</h3>
            <p className="text-gray-400">{item.desc}</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default About
