import React, { createContext, useContext } from "react"
import { ThemeProvider } from "@mui/material/styles"

import rootTheme from "@/themes/rootTheme"
import { AuthProvider } from "./AuthContext"
import { ModalProvider } from "./ModalContext"

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
      <AuthProvider pageProps={props.pageProps}>
        <ModalProvider>
          <ThemeProvider theme={rootTheme}>{props.children}</ThemeProvider>
        </ModalProvider>
      </AuthProvider>
    </RootContext.Provider>
  )
}
