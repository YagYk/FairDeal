import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Sparkles, Github, Twitter, Linkedin, Mail, Heart } from 'lucide-react'

const Footer = () => {
  const currentYear = new Date().getFullYear()

  const footerLinks = [
    {
      title: 'Product',
      links: [
        { name: 'Home', href: '/' },
        { name: 'How It Works', href: '/how-it-works' },
        { name: 'Features', href: '/features' },
      ],
    },
    {
      title: 'Company',
      links: [
        { name: 'About', href: '/about' },
        { name: 'Privacy Policy', href: '#' },
        { name: 'Terms of Service', href: '#' },
      ],
    },
    {
      title: 'Resources',
      links: [
        { name: 'Documentation', href: '#' },
        { name: 'API', href: '#' },
        { name: 'Contact', href: '#' },
      ],
    },
  ]

  const socialLinks = [
    { icon: Github, href: '#', label: 'GitHub' },
    { icon: Twitter, href: '#', label: 'Twitter' },
    { icon: Linkedin, href: '#', label: 'LinkedIn' },
    { icon: Mail, href: '#', label: 'Email' },
  ]

  return (
    <footer className="relative mt-auto border-t border-white/5">
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-t from-dark-950 to-transparent pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-6 py-16">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 lg:gap-8 mb-12">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-6"
            >
              <Link to="/" className="inline-flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-400 via-gold-500 to-amber-600 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-dark-900" />
                </div>
                <span className="text-2xl font-bold text-white">FairDeal</span>
              </Link>
            </motion.div>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="text-gray-400 text-sm leading-relaxed max-w-sm mb-6"
            >
              Empowering professionals with AI-driven contract analysis. 
              Know your worth before you sign.
            </motion.p>
            
            {/* Social Links */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="flex items-center gap-3"
            >
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.href}
                  aria-label={social.label}
                  className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-gray-400 hover:text-gold-400 hover:border-gold-400/30 transition-all duration-300"
                >
                  <social.icon className="w-5 h-5" />
                </a>
              ))}
            </motion.div>
          </div>

          {/* Links Sections */}
          {footerLinks.map((section, sectionIndex) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 * (sectionIndex + 1) }}
            >
              <h3 className="text-white font-semibold mb-4">{section.title}</h3>
              <ul className="space-y-3">
                {section.links.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <Link
                      to={link.href}
                      className="text-gray-400 hover:text-gold-400 transition-colors duration-200 text-sm"
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>

        {/* Bottom Bar */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4"
        >
          <p className="text-gray-500 text-sm flex items-center gap-1">
            © {currentYear} FairDeal. Made with{' '}
            <Heart className="w-4 h-4 text-red-500 fill-red-500" /> for fair workplaces.
          </p>
          <p className="text-gray-600 text-xs">
            Designed for Indian professionals
          </p>
        </motion.div>
      </div>
    </footer>
  )
}

export default Footer
