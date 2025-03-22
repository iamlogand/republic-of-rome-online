"use client"

import { useState } from "react"
import { notFound, useRouter } from "next/navigation"
import toast from "react-hot-toast"

import { useAppContext } from "@/contexts/AppContext"
import getCSRFToken from "@/utils/csrf"
import Breadcrumb from "@/components/Breadcrumb"

interface Error {
  name?: string
}

const NewGamePage = () => {
  const { user, loadingUser } = useAppContext()
  const [name, setName] = useState<string>("")
  const [errors, setErrors] = useState<Error>({})
  const router = useRouter()

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
    }
  }

  if (!user) {
    if (loadingUser) return null
    notFound()
  }

  return (
    <>
      <div className="px-4 lg:px-10 pb-2">
        <Breadcrumb
          items={[
            { href: "/", text: "Home" },
            { href: "/games", text: "Games" },
            { text: "Create new" },
          ]}
        />
      </div>
      <div className="px-4 lg:px-10 py-4 flex flex-col gap-4">
        <h2 className="text-xl">Create new game</h2>
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
              <button
                type="submit"
                className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
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
