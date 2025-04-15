"use client"

import { useState } from "react"

import GoogleLogin from "@/components/GoogleLogin"
import NavBar from "@/components/NavBar"

const LoginPage = () => {
  const [loading, setLoading] = useState(false)

  const handleGoogleLogin = async () => {
    const authStatusResponse = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/auth-status/`,
      {
        credentials: "include",
      },
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
    <>
      <NavBar visible />
      <div className="px-4 py-4 lg:px-10">
        {loading ? (
          <div className="flex justify-center">
            <p>Signing in...</p>
          </div>
        ) : (
          <div className="flex max-w-[800px] flex-col gap-4">
            <h2 className="text-xl">Sign in</h2>
            <p>
              Click the button below to sign in or create a new account for{" "}
              <i>Republic of Rome Online</i>.
            </p>
            <GoogleLogin onClick={handleGoogleLogin} />
            <div className="mt-4 flex flex-col gap-4 rounded bg-neutral-100 px-6 py-4 text-sm">
              <h3 className="text-lg">About</h3>
              <p>
                Currently it&apos;s only possible to create an account by
                signing in with Google. This requires that you share the
                following information with roronline.com:
              </p>
              <ul className="flex list-disc flex-col gap-1 pl-8">
                <li>Name</li>
                <li>Email address</li>
                <li>Profile picture</li>
              </ul>
              <p>How this information is used:</p>
              <ul className="flex list-disc flex-col gap-1 pl-8">
                <li>
                  Your first name is used to generate your initial username, but
                  you can change it at any time. Your username is only visible
                  to other players if you host or join a game.
                </li>
                <li>
                  Your email address is not shared with other players. However,
                  it may be used to contact you regarding gameplay issues, to
                  request feedback, or to inform you about updates and changes
                  to the project.
                </li>
                <li>
                  Your profile picture may be used in the future to personalize
                  your account and display your identity to other players during
                  the game. This feature will be <i>opt-in</i> and never enabled
                  by default.
                </li>
              </ul>
              <p>
                You may delete your account and all associated data at any time.
              </p>
              <p>
                All data is handled responsibly and never shared with third
                parties. Since this is an open-source project, transparency and
                community trust are priorities. If you have any concerns, feel
                free to reach out or review the codebase on{" "}
                <a
                  className="text-blue-600 hover:underline"
                  href="https://github.com/iamlogand/republic-of-rome-online"
                >
                  GitHub
                </a>
                .
              </p>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default LoginPage
