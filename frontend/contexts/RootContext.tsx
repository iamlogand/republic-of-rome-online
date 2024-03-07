import React, { createContext, useContext } from "react"
import { ThemeProvider } from "@mui/material/styles"

import rootTheme from "@/themes/rootTheme"
import { CookieProvider } from "./CookieContext"

const RootContext = createContext({})

export const useRootContext = () => {
  return useContext(RootContext)
}

interface RootProviderProps {
  children: React.ReactNode
  pageProps: any
}

export const RootProvider = (props: RootProviderProps) => {
  return (
    <RootContext.Provider value={{}}>
      <CookieProvider pageProps={props.pageProps}>
        <ThemeProvider theme={rootTheme}>{props.children}</ThemeProvider>
      </CookieProvider>
    </RootContext.Provider>
  )
}
