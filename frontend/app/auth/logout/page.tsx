"use client"

import { useAppContext } from "@/contexts/AppContext"
import { redirect } from "next/navigation"

const LogoutPage = () => {
  const { setUser } = useAppContext()

  const handleLogout = async () => {
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

  return (
    <div className="px-6 py-4 max-w-[800px]">
      <h1 className="text-lg font-bold mb-4">Sign out</h1>
      <button onClick={handleLogout}>Click here to sign out</button>
    </div>
  )
}

export default LogoutPage
