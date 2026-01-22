export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        charcoal: {
          DEFAULT: "#121212",
          light: "#1e1e1e",
          dark: "#0a0a0a",
        },
        gold: {
          DEFAULT: "#D4AF37",
          light: "#F9E076",
          dark: "#996515",
        },
        amber: {
          DEFAULT: "#FFBF00",
          light: "#FFCF40",
          dark: "#CC9900",
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'Inter', 'system-ui', 'sans-serif'],
        serif: ['Crimson Pro', 'Georgia', 'serif'],
      },
      boxShadow: {
        'premium': '0 10px 30px -10px rgba(0, 0, 0, 0.5)',
        'gold-glow': '0 0 20px rgba(212, 175, 55, 0.2)',
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
};
