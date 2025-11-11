/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"], // scannt alle TS/TSX Dateien in src
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
      },
    },
  },
  darkMode: 'media', // nutzt prefers-color-scheme
  plugins: [],
}
