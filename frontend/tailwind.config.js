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

  // Add custom colors
  theme: {
    extend: {
      colors: {
        tyrian: {
          50: "hsl(310, 100%, 97%)",
          100: "hsl(313, 100%, 93%)",
          200: "hsl(316, 80%, 85%)",
          300: "hsl(319, 60%, 75%)",
          400: "hsl(322, 50%, 65%)",
          500: "hsl(325, 40%, 50%)",
          600: "hsl(328, 50%, 40%)",
          700: "hsl(331, 62%, 30%)",
          800: "hsl(334, 80%, 20%)",
          900: "hsl(337, 100%, 15%)",
          950: "hsl(340, 100%, 10%)",
        },
        stone: {
          550: "#67625d",
          650: "#4d4945",
          750: "#353331",
        },
        grayRed: {
          600: "hsl(0, 10%, 32%)",
        },
        grayGreen: {
          600: "hsl(142, 5%, 32%)",
        },
      },
    },
  },

  darkMode: "class",
}
