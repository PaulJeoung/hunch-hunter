/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class', // <-- 이 줄이 반드시 있어야 합니다!
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        dot: ['DungGeunMo', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}