"use client"

import Link from "next/link"
import { notFound } from "next/navigation"

import Breadcrumb from "@/components/Breadcrumb"
import { useAppContext } from "@/contexts/AppContext"

const AccountPage = () => {
  const { user, loadingUser } = useAppContext()

  if (!user) {
    if (loadingUser) return null
    notFound()
  }

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
          <h2 className="text-xl">Your account</h2>
          <Link
            href="/account/edit"
            className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
          >
            Edit
          </Link>
        </div>
        <div className="flex flex-col gap-4">
          <div>
            <h3 className="text-sm pb-2 text-neutral-500">Public</h3>
            <p>
              <span className="inline-block w-[100px]">Username:</span>{" "}
              {user.username}
            </p>
          </div>
          <div>
            <h3 className="text-sm pb-2 text-neutral-500">
              Private (hidden from other players)
            </h3>
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
