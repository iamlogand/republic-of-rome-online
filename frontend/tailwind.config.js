/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],

  // Disable Tailwind CSS's preflight style so Material UI's preflight styles can be used instead
  corePlugins: {
    preflight: false,
  },
}
