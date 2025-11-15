"use client"

import { useState } from "react"
import toast from "react-hot-toast"

import { notFound, useRouter } from "next/navigation"

import Breadcrumb from "@/components/Breadcrumb"
import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"
import getCSRFToken from "@/utils/csrf"

interface Error {
  name?: string
  password?: string
}

const NewGamePage = () => {
  const { user, loadingUser } = useAppContext()
  const [name, setName] = useState<string>("")
  const [password, setPassword] = useState<string>("")
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
        body: JSON.stringify({ name: name, password: password }),
      },
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
      <NavBar visible>
        <Breadcrumb
          items={[
            { href: "/", text: "Home" },
            { href: "/games", text: "Games" },
            { text: "Create new" },
          ]}
        />
      </NavBar>

      <div className="flex flex-col gap-4 px-4 py-4 lg:px-10">
        <h2 className="text-xl">Create new game</h2>
        <form onSubmit={handleSubmit}>
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-baseline">
                <div className="min-w-[180px]">
                  <label htmlFor="username">Game name:</label>
                </div>
                <input
                  id="username"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="min-w-[300px] rounded border border-neutral-600 p-1"
                />
              </div>
              {errors.name && (
                <label className="pl-[150px] text-sm text-red-600">
                  {errors.name}
                </label>
              )}
            </div>
            <div className="flex flex-col gap-1">
              <div className="flex items-baseline">
                <div className="min-w-[180px]">
                  <label htmlFor="username">Password (optional):</label>
                </div>
                <input
                  id="username"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="min-w-[300px] rounded border border-neutral-600 p-1"
                />
              </div>
              {errors.password && (
                <label className="pl-[150px] text-sm text-red-600">
                  {errors.password}
                </label>
              )}
            </div>
            <div className="flex gap-4">
              <button
                type="submit"
                className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
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
