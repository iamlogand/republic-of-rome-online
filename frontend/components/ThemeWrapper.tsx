import { useCookieContext } from "@/contexts/CookieContext"
import { ThemeProvider } from "@emotion/react"
import { ReactNode } from "react"
import darkTheme from "@/themes/darkTheme"
import rootTheme from "@/themes/rootTheme"

interface ThemeWrapperProps {
  children: ReactNode
}

const ThemeWrapper = (props: ThemeWrapperProps) => {
  const { darkMode } = useCookieContext()

  return <ThemeProvider theme={darkMode ? darkTheme : rootTheme}>{props.children}</ThemeProvider>
}

export default ThemeWrapper
