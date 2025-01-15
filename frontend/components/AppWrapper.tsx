"use client"

import React, { ReactNode, useEffect } from "react"

import User from "@/classes/User"
import { useAppContext } from "@/contexts/AppContext"
import Link from "next/link"

interface AppWrapperProps {
  children: ReactNode
}

const AppWrapper = ({ children }: AppWrapperProps): React.JSX.Element => {
  const { user, setUser } = useAppContext()

  useEffect(() => {
    const fetchAuthStatus = async () => {
      const authStatusResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/auth-status/`,
        {
          credentials: "include",
        }
      )
      const responseData = await authStatusResponse.json()
      const csrfToken = responseData.csrftoken
      if (!csrfToken) return

      if (responseData.id) {
        const user = new User(
          responseData.id,
          responseData.username,
          responseData.first_name,
          responseData.last_name,
          responseData.email
        )
        setUser(user)
      }
    }
    fetchAuthStatus()
  }, [])

  return (
    <>
      <header className="px-6 py-4 flex justify-between">
        <Link href="/">
          <h1 className="text-xl font-bold">Republic of Rome Online</h1>
        </Link>
        {user ? (
          <div className="flex gap-8">
            <Link href="/auth/account">
              <div>Welcome, {user.firstName}</div>
            </Link>
            <div>
              <Link href="/auth/logout">Sign out</Link>
            </div>
          </div>
        ) : (
          <div>
            <Link href="/auth/login">Sign in</Link>
          </div>
        )}
      </header>
      <section>{children}</section>
    </>
  )
}

export default AppWrapper
