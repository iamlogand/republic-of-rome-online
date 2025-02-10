"use client"

import React, { ReactNode, useEffect } from "react"

import User from "@/classes/User"
import { useAppContext } from "@/contexts/AppContext"
import Link from "next/link"
import { Toaster } from "react-hot-toast"

interface AppWrapperProps {
  children: ReactNode
}

const AppWrapper = ({ children }: AppWrapperProps): React.JSX.Element => {
  const { user, setUser, setLoadingUser } = useAppContext()

  useEffect(() => {
    const fetchAuthStatus = async () => {
      const authStatusResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/auth-status/`,
        {
          credentials: "include",
        }
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
      <header className="px-6 py-4 flex justify-between items-baseline">
        <Link href="/">
          <h1 className="text-xl font-bold text-[#630330]">
            Republic of Rome Online
          </h1>
        </Link>
        {user ? (
          <div className="flex gap-8">
            <Link href="/games">
              <div className="hover:text-blue-600">Games</div>
            </Link>
            <Link href="/account">
              <div className="hover:text-blue-600">
                Signed in as: <span className="font-bold">{user.username}</span>
              </div>
            </Link>
            <Link href="/auth/logout">
              <div className="hover:text-blue-600">Sign out</div>
            </Link>
          </div>
        ) : (
          <Link href="/auth/login">
            <div className="hover:text-blue-600">Sign in</div>
          </Link>
        )}
      </header>
      <section>{children}</section>
    </>
  )
}

export default AppWrapper
