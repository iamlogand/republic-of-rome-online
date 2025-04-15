"use client"

import { redirect } from "next/navigation"
import { useEffect } from "react"

import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"

const LogoutPage = () => {
  const { setUser } = useAppContext()

  useEffect(() => {
    const logoutUser = async () => {
      const authStatusResponse = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/auth-status/`,
        {
          credentials: "include",
        },
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
        },
      )
      setUser(undefined)
      redirect("/")
    }
    logoutUser()
  }, [setUser])

  return (
    <>
      <NavBar visible />
      <div className="flex justify-center px-4 py-4 lg:px-10">
        <p>Signing out...</p>
      </div>
    </>
  )
}

export default LogoutPage
