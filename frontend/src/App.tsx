import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { AuthProvider } from './contexts/AuthContext'
import Header from './components/Header'
import Footer from './components/Footer'
import Home from './pages/Home'
import HowItWorks from './pages/HowItWorks'
import Features from './pages/Features'
import About from './pages/About'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Profile from './pages/Profile'
import Developer from './pages/Developer'
import NotFound from './pages/NotFound'
import ErrorBoundary from './components/ErrorBoundary'
import ProtectedRoute from './components/ProtectedRoute'

function AppRoutes() {
  const location = useLocation()
  const showFooter = !['/', '/login', '/signup'].includes(location.pathname)

  return (
    <div className="min-h-screen relative overflow-x-hidden flex flex-col">
      <Header />
      <main className="flex-1 w-full">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Routes location={location}>
              <Route path="/" element={<Home />} />
              <Route path="/how-it-works" element={<HowItWorks />} />
              <Route path="/features" element={<Features />} />
              <Route path="/about" element={<About />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/developer"
                element={
                  <ProtectedRoute>
                    <Developer />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </motion.div>
        </AnimatePresence>
      </main>
      {showFooter && <Footer />}
    </div>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App

