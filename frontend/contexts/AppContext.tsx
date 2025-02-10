"use client"

import React, { createContext, useContext, useState, ReactNode } from "react"

import User from "@/classes/User"

interface AppContextType {
  user: User | undefined
  setUser: (user: User | undefined) => void
  loadingUser: boolean
  setLoadingUser: (loadingUser: boolean) => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider = ({
  children,
}: AppProviderProps): React.JSX.Element => {
  const [user, setUser] = useState<User | undefined>(undefined)
  const [loadingUser, setLoadingUser] = useState<boolean>(true)

  return (
    <AppContext.Provider value={{ user, setUser, loadingUser, setLoadingUser }}>
      {children}
    </AppContext.Provider>
  )
}

export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error("useAppProvider must be used within an AppProvider")
  }
  return context
}
