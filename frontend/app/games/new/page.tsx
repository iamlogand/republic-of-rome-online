"use client"

import Link from "next/link"
import { useState } from "react"

import { useAppContext } from "@/contexts/AppContext"
import getCSRFToken from "@/utils/csrf"
import { useRouter } from "next/navigation"
import Breadcrumb from "@/components/Breadcrumb"
import toast from "react-hot-toast"

interface Error {
  name?: string
}

const NewGamePage = () => {
  const { user } = useAppContext()
  const [name, setName] = useState<string>("")
  const [errors, setErrors] = useState<Error>({})
  const router = useRouter()

  if (!user) return null

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ name: name }),
      }
    )
    const data = await response.json()
    if (response.ok) {
      toast.success("Created new game")
      router.push(`/games/${data.id}`)
    } else {
      setErrors(data)
      console.error(data)
      toast.error("Something went wrong")
    }
  }

  return (
    <>
      <div className="px-6 pb-2">
        <Breadcrumb
          items={[
            { href: "/", text: "Home" },
            { href: "/games", text: "Games" },
            { text: "Create new" },
          ]}
        />
      </div>
      <div className="px-6 py-4 flex flex-col gap-4">
        <h1 className="text-xl">Create new game</h1>
        <form onSubmit={handleSubmit}>
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-baseline">
                <div className="min-w-[150px]">
                  <label htmlFor="username">Game name:</label>
                </div>
                <input
                  id="username"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="min-w-[300px] p-1 border border-neutral-600 rounded"
                />
              </div>
              {errors.name && (
                <label className="pl-[150px] text-sm text-red-600">
                  {errors.name}
                </label>
              )}
            </div>
            <div className="flex gap-4">
              <Link
                href="/games"
                className="px-2 py-1 text-neutral-600 border border-neutral-600 rounded-md hover:bg-neutral-100"
              >
                Back
              </Link>
              <button
                type="submit"
                className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
              >
                Create
              </button>
            </div>
          </div>
        </form>
      </div>
    </>
  )
}

export default NewGamePage
