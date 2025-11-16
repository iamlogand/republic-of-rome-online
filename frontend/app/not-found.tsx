"use client"

import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"

const NotFound = () => {
  const { user } = useAppContext()

  return (
    <>
      <NavBar visible></NavBar>
      <div className="flex w-full flex-col items-center gap-4 pt-16">
        <h2>404 - Page not found</h2>
        <p className="text-center text-neutral-600">
          {user ? (
            <>
              Either this page doesn&apos;t exist, or you don&apos;t have
              permission to access it
            </>
          ) : (
            <>
              Either this page doesn&apos;t exist, or you need to sign in to
              access it
            </>
          )}
        </p>
      </div>
    </>
  )
}
export default NotFound
