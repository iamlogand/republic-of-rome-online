"use client"

import { redirect } from "next/navigation"

const AuthCallbackPage = () => {
  redirect("/auth/account")
}

export default AuthCallbackPage
