/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-primary': '#FF5A5F',
        'brand-secondary': '#00A699',
        'brand-dark': '#484848',
        'brand-light': '#767676',
        'brand-bg': '#F7F7F7',
      },
      fontFamily: {
        sans: ['Circular', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 6px 16px rgba(0, 0, 0, 0.12)',
        'nav': '0 1px 12px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [],
}
