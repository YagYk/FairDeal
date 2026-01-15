/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dark': {
          '950': '#000000',
          '900': '#050505',
          '800': '#0a0a0a',
          '700': '#121212',
          '600': '#1a1a1a',
          '500': '#262626',
          '400': '#333333',
          'brown': '#2a1a0a',
          'glass': 'rgba(0, 0, 0, 0.7)',
        },
        'gold': {
          '200': '#FEF3C7',
          '300': '#FDE68A',
          '400': '#D4AF37',
          '500': '#C5A028',
          '600': '#B8941E',
          '700': '#92740F',
          'glow': 'rgba(212, 175, 55, 0.5)',
        },
        'accent': {
          'purple': '#8B5CF6',
          'blue': '#3B82F6',
          'cyan': '#06B6D4',
          'emerald': '#10B981',
          'rose': '#F43F5E',
        }
      },
      fontFamily: {
        'sans': ['DM Sans', 'Inter', 'system-ui', 'sans-serif'],
        'serif': ['Crimson Pro', 'Georgia', 'serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'metallic': 'linear-gradient(135deg, #DFBD69 0%, #926F34 50%, #DFBD69 100%)',
        'hero-gradient': 'linear-gradient(180deg, rgba(212, 175, 55, 0.05) 0%, transparent 50%)',
        'card-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0) 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
        'slide-up': 'slideUp 0.5s ease-out',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 3s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'spin-slow': 'spin 20s linear infinite',
        'pulse-slow': 'pulse 4s ease-in-out infinite',
        'bounce-slow': 'bounce 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(212,175,55,0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(212,175,55,0.6), 0 0 10px rgba(212,175,55,0.4)' },
        },
      },
      boxShadow: {
        'glow-gold': '0 0 20px rgba(212, 175, 55, 0.3)',
        'glow-gold-lg': '0 0 40px rgba(212, 175, 55, 0.4)',
        'inner-glow': 'inset 0 0 20px rgba(212, 175, 55, 0.1)',
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
    },
  },
  plugins: [],
}
