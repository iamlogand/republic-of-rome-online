import type { Preview } from "@storybook/react"
import "../app/globals.css"

// Match the font loaded in app/layout.tsx so component metrics are consistent
const link = document.createElement("link")
link.rel = "stylesheet"
link.href =
  "https://fonts.googleapis.com/css2?family=Open+Sans&display=swap"
document.head.appendChild(link)

const style = document.createElement("style")
style.textContent = "body { font-family: 'Open Sans', sans-serif; }"
document.head.appendChild(style)

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
}

export default preview
