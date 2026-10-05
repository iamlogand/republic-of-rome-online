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
        "log-slide-in": {
          "0%": {
            transform: "translateY(10px)",
            opacity: "0",
            backgroundColor: "rgb(254 240 138)",
          },
          "20%": {
            transform: "translateY(0)",
            opacity: "1",
            backgroundColor: "rgb(254 240 138)",
          },
          "100%": {
            transform: "translateY(0)",
            opacity: "1",
            backgroundColor: "transparent",
          },
        },
      },
      animation: {
        "log-slide-in": "log-slide-in 1.5s ease-out forwards",
      },
    },
  },
  plugins: [],
} satisfies Config
