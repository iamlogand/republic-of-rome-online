"use client"

import { useEffect } from "react"

import { useRouter } from "next/navigation"

import NavBar from "@/components/NavBar"

const AuthCallbackPage = () => {
  const router = useRouter()

  useEffect(() => {
    const redirectUrl = localStorage.getItem("post_auth_redirect")

    localStorage.removeItem("post_auth_redirect")

    if (redirectUrl && redirectUrl.startsWith("/")) {
      router.push(redirectUrl)
    } else {
      router.push("/")
    }
  }, [router])

  return (
    <>
      <NavBar visible />
      <div className="px-4 py-4">
        <div className="flex justify-center">
          <p>Redirecting...</p>
        </div>
      </div>
    </>
  )
}

export default AuthCallbackPage
