"use client"

import { useEffect } from "react"

import { usePathname, useRouter } from "next/navigation"

import { useAppContext } from "@/contexts/AppContext"

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, loadingUser } = useAppContext()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!loadingUser && !user) {
      localStorage.setItem("post_auth_redirect", pathname)
      router.replace("/auth/login")
    }
  }, [user, loadingUser, router, pathname])

  if (loadingUser || !user) return null

  return <>{children}</>
}
