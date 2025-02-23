"use client"

import { useAppContext } from "@/contexts/AppContext"

const NotFound = () => {
  const { user } = useAppContext()

  return (
    <div className="w-full pt-16 flex flex-col gap-4 items-center">
      <h2>404 - Page Not Found</h2>
      <p className="text-neutral-500 text-center">
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
  )
}
export default NotFound
