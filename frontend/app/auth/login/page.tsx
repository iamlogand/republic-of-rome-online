"use client"

import { useState } from "react"
import GoogleLogin from "@/components/GoogleLogin"

const LoginPage = () => {
  const [loading, setLoading] = useState(false)

  const handleGoogleLogin = async () => {
    const authStatusResponse = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/auth-status/`,
      {
        credentials: "include",
      }
    )
    const responseData = await authStatusResponse.json()
    const csrfToken = responseData.csrftoken
    if (!csrfToken) return

    const form = document.createElement("form")
    form.method = "POST"
    form.action = `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/_allauth/browser/v1/auth/provider/redirect`

    const providerInput = document.createElement("input")
    providerInput.type = "hidden"
    providerInput.name = "provider"
    providerInput.value = "google"

    const callbackUrlInput = document.createElement("input")
    callbackUrlInput.type = "hidden"
    callbackUrlInput.name = "callback_url"
    callbackUrlInput.value = "/login-callback/"

    const processInput = document.createElement("input")
    processInput.type = "hidden"
    processInput.name = "process"
    processInput.value = "login"

    const csrfInput = document.createElement("input")
    csrfInput.type = "hidden"
    csrfInput.name = "csrfmiddlewaretoken"
    csrfInput.value = csrfToken

    form.appendChild(providerInput)
    form.appendChild(callbackUrlInput)
    form.appendChild(processInput)
    form.appendChild(csrfInput)

    document.body.appendChild(form)
    form.submit()
    setLoading(true)
  }

  return (
    <div className="px-6 py-4">
      {loading ? (
        <div className="flex justify-center">
          <p>Signing in...</p>
        </div>
      ) : (
        <>
          <h2 className="text-lg font-bold mb-4">Sign in</h2>
          <GoogleLogin onClick={handleGoogleLogin} />
        </>
      )}
    </div>
  )
}

export default LoginPage
