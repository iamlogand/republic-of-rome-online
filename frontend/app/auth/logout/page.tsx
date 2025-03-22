"use client"

import { useAppContext } from "@/contexts/AppContext"
import { redirect } from "next/navigation"
import { useEffect } from "react"

const LogoutPage = () => {
  const { setUser } = useAppContext()

  useEffect(() => {
    const logoutUser = async () => {
      const authStatusResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/auth-status/`,
        {
          credentials: "include",
        }
      )
      const responseData = await authStatusResponse.json()
      const csrfToken = responseData.csrftoken
      if (!csrfToken) return

      await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/_allauth/browser/v1/auth/session`,
        {
          method: "DELETE",
          credentials: "include",
          headers: {
            "X-CSRFToken": csrfToken,
          },
        }
      )
      setUser(undefined)
      redirect("/")
    }
    logoutUser()
  }, [setUser])

  return (
    <div className="px-4 lg:px-10 py-4 flex justify-center">
      <p>Signing out...</p>
    </div>
  )
}

export default LogoutPage
