/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./agentpm/web/templates/**/*.{html,js}",
    "./agentpm/web/static/js/**/*.js",
    "./docs/**/*.{md,html}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      // Tailwind v4: Minimal config - most theming done via @theme directive in CSS
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', '"Fira Code"', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};