import type { Config } from "tailwindcss"

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      keyframes: {
        highlight: {
          "0%": {
            backgroundColor: "rgb(254 240 138)",
          },
          "20%": {
            backgroundColor: "rgb(254 240 138)",
          },
          "100%": {
            backgroundColor: "transparent",
          },
        },
      },
      animation: {
        highlight: "highlight 1.5s ease-out forwards",
      },
    },
  },
  plugins: [],
} satisfies Config
