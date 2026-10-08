/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // support class-based dark mode switching
  theme: {
    extend: {
      colors: {
        primary: {
          light: '#2e7d32', // Emerald Forest Green
          DEFAULT: '#1b5e20',
          dark: '#0d3c12',
        },
        secondary: {
          light: '#d7ccc8', // Sand Earthy Grey
          DEFAULT: '#8d6e63',
          dark: '#4e342e',
        },
        accent: {
          gold: '#fbc02d',
          amber: '#ff6f00',
        },
        dark: {
          bg: '#0b130e',      // Deep charcoal/moss background
          surface: '#121e16', // Slightly lighter moss container
          border: '#1f3326',
        }
      },
      fontFamily: {
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  plugins: [],
}
