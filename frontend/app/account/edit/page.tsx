"use client"

import { useAppContext } from "@/contexts/AppContext"
import { useEffect, useState } from "react"

import User from "@/classes/User"
import getCSRFToken from "@/utils/csrf"
import Breadcrumb from "@/components/Breadcrumb"
import toast from "react-hot-toast"
import { useRouter } from "next/navigation"

interface ResponseError {
  username?: string
}

const AccountEditPage = () => {
  const { user, setUser } = useAppContext()
  const [newUsername, setNewUsername] = useState<string>("")
  const [errors, setErrors] = useState<ResponseError>({})
  const router = useRouter()

  useEffect(() => {
    if (user) setNewUsername(user.username)
  }, [user, setNewUsername])

  if (!user) return null

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/users/${user.id}/`,
      {
        method: "PUT",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ username: newUsername }),
      }
    )
    const data = await response.json()
    if (response.ok) {
      const updatedUser = new User(data)
      setUser(updatedUser)
      toast.success("Account saved")
      router.push("/account")
    } else {
      setErrors(data)
    }
  }

  const handleDeleteClick = async () => {
    const userConfirmed = window.confirm(
      `Are you sure you want to permanently delete your account?`
    )
    if (!userConfirmed) return

    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/users/${user.id}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      }
    )
    if (response.ok) {
      toast.success("Account deleted")
      router.push("/auth/logout")
    }
  }

  return (
    <>
      <div className="px-6 pb-2">
        <Breadcrumb
          items={[
            { href: "/", text: "Home" },
            { href: "/account", text: "Your account" },
            { text: "Edit" },
          ]}
        />
      </div>
      <hr className="border-neutral-300" />
      <div className="px-6 py-4 flex flex-col gap-4">
        <h2 className="text-xl">Edit your account</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <div className="flex items-baseline">
              <div className="min-w-[100px]">
                <label htmlFor="username">Username:</label>
              </div>
              <input
                id="username"
                type="text"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                className="w-[300px] p-1 border border-neutral-600 rounded"
              />
            </div>
            {errors.username && (
              <label className="pl-[100px] text-sm text-red-600">
                {errors.username}
              </label>
            )}
          </div>
          <div className="flex">
            <button
              type="submit"
              className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
            >
              Save changes
            </button>
          </div>
        </form>
        <div className="mt-10 flex flex-col gap-2 items-start">
          <h3 className="text-xl">Delete your account</h3>
          <button
            onClick={handleDeleteClick}
            className="px-2 py-1 text-red-600 border border-red-600 rounded-md hover:bg-red-100"
          >
            Permanently delete account
          </button>
        </div>
      </div>
    </>
  )
}

export default AccountEditPage
