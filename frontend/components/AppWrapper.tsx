"use client"

import React, { ReactNode, useEffect } from "react"
import { Toaster } from "react-hot-toast"

import User from "@/classes/User"
import { useAppContext } from "@/contexts/AppContext"

interface AppWrapperProps {
  children: ReactNode
}

const AppWrapper = ({ children }: AppWrapperProps): React.JSX.Element => {
  const { setUser, setLoadingUser } = useAppContext()

  useEffect(() => {
    const fetchAuthStatus = async () => {
      const authStatusResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/auth-status/`,
        {
          credentials: "include",
        },
      )
      const data = await authStatusResponse.json()
      if (data.csrftoken && data.id) {
        const user = new User(data)
        setUser(user)
      }
      setLoadingUser(false)
    }
    fetchAuthStatus()
  }, [setUser, setLoadingUser])

  return (
    <>
      <Toaster />
      <section className="w-full">{children}</section>
    </>
  )
}

export default AppWrapper
