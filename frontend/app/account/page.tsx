"use client"

import { useAppContext } from "@/contexts/AppContext"
import Link from "next/link"

const AccountPage = () => {
  const { user } = useAppContext()

  if (!user) return null

  return (
    <div className="px-6 py-4 max-w-[800px]">
      <div className="pb-4 flex gap-8 items-baseline">
        <h1 className="text-xl font-bold">Your account</h1>
        <Link
          href="/account/edit"
          className="px-2 py-1 text-blue-700 border border-blue-700 rounded-md"
        >
          Edit
        </Link>
      </div>
      {user && (
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="text-sm pb-2 text-neutral-700">Public</h2>
            <p>
              <span className="inline-block w-[100px]">Username:</span>{" "}
              {user.username}
            </p>
          </div>
          <div>
            <h2 className="text-sm pb-2 text-neutral-700">
              Private (hidden from other players)
            </h2>
            <p>
              <span className="inline-block w-[100px]">First name:</span>{" "}
              {user.firstName}
            </p>
            <p>
              <span className="inline-block w-[100px]">Last name:</span>{" "}
              {user.lastName}
            </p>
            <p>
              <span className="inline-block w-[100px]">Email:</span>{" "}
              {user.email}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default AccountPage
