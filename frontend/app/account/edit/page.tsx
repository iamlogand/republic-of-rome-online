"use client"

import { useAppContext } from "@/contexts/AppContext"
import Link from "next/link"
import { useState } from "react"

import User from "@/classes/User"

const AccountEditPage = () => {
  const { user, setUser } = useAppContext()
  const [newUsername, setNewUsername] = useState<string>("")
  const [error, setError] = useState<string>("")

  const getCSRFToken = () => {
    const csrfCookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
    return csrfCookie ? csrfCookie.split("=")[1] : ""
  }

  if (!user) return null

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()

    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/user/${user.id}/`,
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
      const updatedUser = new User(
        data.id,
        data.username,
        data.first_name,
        data.last_name,
        data.email
      )
      setUser(updatedUser)
    } else {
      setError(data.username)
    }
  }

  return (
    <div className="px-6 py-4 max-w-[800px]">
      <h1 className="pb-4 text-xl font-bold">Edit your account</h1>
      <form onSubmit={handleSubmit}>
        <div className="pb-4 flex flex-col gap-4">
          <div className="flex items-baseline">
            <div className="min-w-[150px]">Current username:</div>
            <div className="p-1">{user.username}</div>
          </div>
          <label>
            <div className="flex items-baseline">
              <div className="min-w-[150px]">New username:</div>
              <input
                type="text"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                className="p-1 border border-neutral-700 rounded"
              />
            </div>
          </label>
          {error && <div className="text-sm text-red-700">{error}</div>}
        </div>
        <div className="flex gap-4">
          <Link
            href="/account"
            className="px-2 py-1 text-neutral-700 border border-neutral-700 rounded-md"
          >
            Back
          </Link>
          <button
            type="submit"
            className="px-2 py-1 text-blue-700 border border-blue-700 rounded-md"
          >
            Update
          </button>
        </div>
      </form>
    </div>
  )
}

export default AccountEditPage
