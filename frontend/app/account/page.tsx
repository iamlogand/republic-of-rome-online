"use client"

import Link from "next/link"
import { notFound } from "next/navigation"

import Breadcrumb from "@/components/Breadcrumb"
import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"

const AccountPage = () => {
  const { user, loadingUser } = useAppContext()

  if (!user) {
    if (loadingUser) return null
    notFound()
  }

  return (
    <>
      <NavBar
        visible
        children={
          <Breadcrumb
            items={[{ href: "/", text: "Home" }, { text: "Your account" }]}
          />
        }
      />
      <div className="flex flex-col gap-4 px-4 py-4 lg:px-10">
        <div className="flex items-baseline gap-8">
          <h2 className="text-xl">Your account</h2>
          <Link
            href="/account/edit"
            className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
          >
            Edit
          </Link>
        </div>
        <div className="flex flex-col gap-4">
          <div>
            <h3 className="pb-2 text-sm text-neutral-600">Public</h3>
            <p>
              <span className="inline-block w-[100px]">Username:</span>{" "}
              {user.username}
            </p>
          </div>
          <div>
            <h3 className="pb-2 text-sm text-neutral-600">
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
