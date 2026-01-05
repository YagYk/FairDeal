import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, User } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const Header = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/how-it-works', label: 'How It Works' },
    { path: '/features', label: 'Features' },
    { path: '/about', label: 'About' },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <>
      {/* iOS 26 Liquid Glass Navbar - Fixed at Bottom Center */}
      <motion.nav
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20, delay: 0.2 }}
        className="fixed bottom-4 md:bottom-6 left-1/2 -translate-x-1/2 z-50"
        style={{ width: 'fit-content', maxWidth: '95vw' }}
      >
        <div
          className="liquid-glass rounded-[28px] px-4 sm:px-6 py-2 sm:py-3 flex items-center justify-center gap-2 sm:gap-4"
          style={{
            background: `rgba(255, 255, 255, ${0.03 + Math.min(scrollY / 500, 0.05)})`,
          }}
        >
          {/* Desktop Navigation - Centered */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link key={item.path} to={item.path}>
                <motion.div
                  className="relative px-4 py-2 rounded-full group"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isActive(item.path) && (
                    <motion.div
                      layoutId="activeNavBg"
                      className="absolute inset-0 rounded-full bg-white/10 backdrop-blur-sm"
                      transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                    />
                  )}
                  <span
                    className={`relative z-10 text-sm font-medium transition-colors duration-200 ${isActive(item.path)
                      ? 'text-gold-400'
                      : 'text-white/70 group-hover:text-white'
                      }`}
                  >
                    {item.label}
                  </span>
                </motion.div>
              </Link>
            ))}
          </nav>

          {/* User Menu / Auth Buttons */}
          <div className="hidden md:flex items-center ml-2 gap-2 lg:gap-3">
            {isAuthenticated ? (
              <div className="relative">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="liquid-glass rounded-full p-2 flex items-center justify-center hover:bg-white/10 transition-all"
                >
                  <User className="w-5 h-5 text-white/70" />
                </motion.button>
                <AnimatePresence>
                  {isUserMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      className="absolute bottom-full right-0 mb-2 liquid-glass rounded-2xl p-4 min-w-[200px]"
                    >
                      <div className="mb-3 pb-3 border-b border-white/10">
                        <p className="text-white font-semibold text-sm">{user?.name}</p>
                        <p className="text-gray-400 text-xs">{user?.email}</p>
                      </div>
                      <Link to="/profile">
                        <motion.div
                          whileTap={{ scale: 0.98 }}
                          onClick={() => setIsUserMenuOpen(false)}
                          className="px-3 py-2 rounded-lg hover:bg-white/5 text-white text-sm cursor-pointer mb-2"
                        >
                          Profile
                        </motion.div>
                      </Link>
                      <Link to="/developer">
                        <motion.div
                          whileTap={{ scale: 0.98 }}
                          onClick={() => setIsUserMenuOpen(false)}
                          className="px-3 py-2 rounded-lg hover:bg-white/5 text-white text-sm cursor-pointer mb-2"
                        >
                          Developer
                        </motion.div>
                      </Link>
                      <motion.div
                        whileTap={{ scale: 0.98 }}
                        onClick={() => {
                          logout()
                          setIsUserMenuOpen(false)
                          navigate('/')
                        }}
                        className="px-3 py-2 rounded-lg hover:bg-red-500/10 text-red-400 text-sm cursor-pointer"
                      >
                        Sign Out
                      </motion.div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <>
                <Link to="/login">
                  <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    className="text-sm font-medium px-4 py-2 rounded-full text-white/70 hover:text-white transition-colors"
                  >
                    Sign In
                  </motion.button>
                </Link>
                <Link to="/">
                  <motion.button
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    className="text-sm font-semibold px-5 py-2 rounded-full bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900 shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-shadow"
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

          {/* Mobile Toggle */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden p-2 rounded-full bg-white/5 text-white/70 hover:text-white hover:bg-white/10 transition-all"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu Dropdown */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              className="mt-3 liquid-glass rounded-2xl p-4 md:hidden"
            >
              <div className="flex flex-col gap-2">
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <motion.div
                      whileTap={{ scale: 0.98 }}
                      className={`px-4 py-3 rounded-xl text-sm font-medium transition-all ${isActive(item.path)
                        ? 'bg-gold-500/10 text-gold-400'
                        : 'text-white/70 hover:bg-white/5 hover:text-white'
                        }`}
                    >
                      {item.label}
                    </motion.div>
                  </Link>
                ))}
                <Link to="/" onClick={() => setIsMobileMenuOpen(false)}>
                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    className="mt-2 w-full text-sm font-semibold px-5 py-3 rounded-xl bg-gradient-to-r from-gold-500 to-amber-500 text-dark-900"
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
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.nav>
    </>
  )
}

export default Header
