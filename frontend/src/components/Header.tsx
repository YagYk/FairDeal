import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, User, Sparkles, ChevronDown } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const Header = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [location.pathname])

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/how-it-works', label: 'How It Works' },
    { path: '/features', label: 'Features' },
    { path: '/about', label: 'About' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <>
      {/* Fixed Top Navigation */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled 
            ? 'bg-dark-900/90 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20' 
            : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <motion.div
                whileHover={{ rotate: 10, scale: 1.05 }}
                className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-400 via-gold-500 to-amber-600 flex items-center justify-center shadow-lg shadow-gold-500/20"
              >
                <Sparkles className="w-5 h-5 text-dark-900" />
              </motion.div>
              <span className="text-xl font-bold text-white group-hover:text-gold-400 transition-colors">
                FairDeal
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => (
                <Link key={item.path} to={item.path}>
                  <motion.div
                    className="relative px-4 py-2 rounded-lg group"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {isActive(item.path) && (
                      <motion.div
                        layoutId="activeNavBg"
                        className="absolute inset-0 rounded-lg bg-gold-500/10 border border-gold-500/20"
                        transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                      />
                    )}
                    <span
                      className={`relative z-10 text-sm font-medium transition-colors duration-200 ${
                        isActive(item.path)
                          ? 'text-gold-400'
                          : 'text-gray-400 group-hover:text-white'
                      }`}
                    >
                      {item.label}
                    </span>
                  </motion.div>
                </Link>
              ))}
            </nav>

            {/* Right Section - Auth Buttons */}
            <div className="hidden md:flex items-center gap-3">
              {isAuthenticated ? (
                <div className="relative">
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-amber-500 flex items-center justify-center">
                      <User className="w-4 h-4 text-dark-900" />
                    </div>
                    <span className="text-sm text-white font-medium max-w-[100px] truncate">
                      {user?.name || 'User'}
                    </span>
                    <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''}`} />
                  </motion.button>

                  {/* User Dropdown */}
                  <AnimatePresence>
                    {isUserMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.15 }}
                        className="absolute top-full right-0 mt-2 w-56 bg-dark-800/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-xl overflow-hidden"
                      >
                        <div className="p-4 border-b border-white/5">
                          <p className="text-white font-semibold text-sm truncate">{user?.name}</p>
                          <p className="text-gray-500 text-xs truncate">{user?.email}</p>
                        </div>
                        <div className="p-2">
                          <Link to="/profile" onClick={() => setIsUserMenuOpen(false)}>
                            <motion.div
                              whileTap={{ scale: 0.98 }}
                              className="px-3 py-2.5 rounded-lg hover:bg-white/5 text-gray-300 hover:text-white text-sm cursor-pointer transition-colors"
                            >
                              Profile
                            </motion.div>
                          </Link>
                          <Link to="/developer" onClick={() => setIsUserMenuOpen(false)}>
                            <motion.div
                              whileTap={{ scale: 0.98 }}
                              className="px-3 py-2.5 rounded-lg hover:bg-white/5 text-gray-300 hover:text-white text-sm cursor-pointer transition-colors"
                            >
                              Developer
                            </motion.div>
                          </Link>
                          <div className="my-1 border-t border-white/5" />
                          <motion.div
                            whileTap={{ scale: 0.98 }}
                            onClick={() => {
                              logout()
                              setIsUserMenuOpen(false)
                              navigate('/')
                            }}
                            className="px-3 py-2.5 rounded-lg hover:bg-red-500/10 text-red-400 text-sm cursor-pointer transition-colors"
                          >
                            Sign Out
                          </motion.div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <>
                  <Link to="/login">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="text-sm font-medium px-4 py-2 rounded-lg text-gray-400 hover:text-white transition-colors"
                    >
                      Sign In
                    </motion.button>
                  </Link>
                  <Link to="/">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="text-sm font-semibold px-5 py-2.5 rounded-lg bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all"
                      onClick={(e) => {
                        if (location.pathname === '/') {
                          e.preventDefault()
                          window.scrollTo({ top: 0, behavior: 'smooth' })
                        }
                      }}
                    >
                      Get Started
                    </motion.button>
                  </Link>
                </>
              )}
            </div>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="md:hidden border-t border-white/5 bg-dark-900/95 backdrop-blur-xl overflow-hidden"
            >
              <div className="px-4 py-4 space-y-1">
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <motion.div
                      whileTap={{ scale: 0.98 }}
                      className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                        isActive(item.path)
                          ? 'bg-gold-500/10 text-gold-400 border border-gold-500/20'
                          : 'text-gray-400 hover:bg-white/5 hover:text-white'
                      }`}
                    >
                      {item.label}
                    </motion.div>
                  </Link>
                ))}
                
                <div className="pt-4 mt-4 border-t border-white/5 space-y-2">
                  {isAuthenticated ? (
                    <>
                      <div className="px-4 py-2 mb-2">
                        <p className="text-white font-semibold text-sm">{user?.name}</p>
                        <p className="text-gray-500 text-xs">{user?.email}</p>
                      </div>
                      <Link to="/profile" onClick={() => setIsMobileMenuOpen(false)}>
                        <motion.div
                          whileTap={{ scale: 0.98 }}
                          className="px-4 py-3 rounded-lg text-sm font-medium text-gray-400 hover:bg-white/5 hover:text-white transition-all"
                        >
                          Profile
                        </motion.div>
                      </Link>
                      <Link to="/developer" onClick={() => setIsMobileMenuOpen(false)}>
                        <motion.div
                          whileTap={{ scale: 0.98 }}
                          className="px-4 py-3 rounded-lg text-sm font-medium text-gray-400 hover:bg-white/5 hover:text-white transition-all"
                        >
                          Developer
                        </motion.div>
                      </Link>
                      <motion.button
                        whileTap={{ scale: 0.98 }}
                        onClick={() => {
                          logout()
                          setIsMobileMenuOpen(false)
                          navigate('/')
                        }}
                        className="w-full px-4 py-3 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition-all text-left"
                      >
                        Sign Out
                      </motion.button>
                    </>
                  ) : (
                    <>
                      <Link to="/login" onClick={() => setIsMobileMenuOpen(false)}>
                        <motion.div
                          whileTap={{ scale: 0.98 }}
                          className="px-4 py-3 rounded-lg text-sm font-medium text-gray-400 hover:bg-white/5 hover:text-white transition-all"
                        >
                          Sign In
                        </motion.div>
                      </Link>
                      <Link to="/" onClick={() => setIsMobileMenuOpen(false)}>
                        <motion.button
                          whileTap={{ scale: 0.98 }}
                          className="w-full px-4 py-3 rounded-lg text-sm font-semibold bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 shadow-lg shadow-gold-500/20"
                          onClick={(e) => {
                            if (location.pathname === '/') {
                              e.preventDefault()
                              window.scrollTo({ top: 0, behavior: 'smooth' })
                            }
                          }}
                        >
                          Get Started
                        </motion.button>
                      </Link>
                    </>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.header>

      {/* Spacer to prevent content from going under fixed header */}
      <div className="h-16 md:h-20" />
    </>
  )
}

export default Header
