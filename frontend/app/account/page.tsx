"use client"

import Breadcrumb from "@/components/Breadcrumb"
import { useAppContext } from "@/contexts/AppContext"
import Link from "next/link"

const AccountPage = () => {
  const { user } = useAppContext()

  if (!user) return null

  return (
    <>
      <div className="px-6 pb-2">
        <Breadcrumb
          items={[{ href: "/", text: "Home" }, { text: "Your account" }]}
        />
      </div>
      <hr className="border-neutral-300" />
      <div className="px-6 py-4 flex flex-col gap-4">
        <div className="flex gap-8 items-baseline">
          <h1 className="text-xl">Your account</h1>
          <Link
            href="/account/edit"
            className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
          >
            Edit
          </Link>
        </div>
        <div className="flex flex-col gap-4">
          <div>
            <h2 className="text-sm pb-2 text-neutral-600">Public</h2>
            <p>
              <span className="inline-block w-[100px]">Username:</span>{" "}
              {user.username}
            </p>
          </div>
          <div>
            <h2 className="text-sm pb-2 text-neutral-600">
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
      </div>
    </>
  )
}

export default AccountPage
