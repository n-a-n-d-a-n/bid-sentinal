/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          500: '#102a43',
          800: '#0b1b2b',
          900: '#06101e',
          950: '#030811',
        },
        navy: {
          800: '#0f172a',
          900: '#090d16',
          950: '#04060a',
        },
        slate: {
          850: '#141e2e',
          900: '#0f172a',
          950: '#020617',
        },
        accent: {
          blue: '#3b82f6',
          cyan: '#06b6d4',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#f43f5e',
        }
      },
      fontFamily: {
        sans: ['"Google Sans"', '"Google Sans Text"', '"Product Sans"', 'sans-serif'],
        mono: ['"Google Sans"', '"Google Sans Text"', '"Product Sans"', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
