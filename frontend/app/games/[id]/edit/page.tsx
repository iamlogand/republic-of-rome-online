"use client"

import { useCallback, useEffect, useState } from "react"
import toast from "react-hot-toast"

import { notFound, useParams, useRouter } from "next/navigation"

import Game, { GameData } from "@/classes/Game"
import Breadcrumb from "@/components/Breadcrumb"
import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"
import getCSRFToken from "@/utils/csrf"

interface ResponseError {
  name?: string
  password?: string
}

const EditGamePage = () => {
  const router = useRouter()

  const { user, loadingUser } = useAppContext()
  const [game, setGame] = useState<Game | undefined>()
  const [name, setName] = useState<string>("")
  const [password, setPassword] = useState<string>("")
  const [errors, setErrors] = useState<ResponseError>({})

  const params = useParams()

  const fetchGame = useCallback(async () => {
    setGame(undefined)
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${params.id}`,
      {
        credentials: "include",
      },
    )
    const data: GameData = await response.json()
    const game = new Game(data)
    setGame(game)
    setName(game.name)
    setPassword(game.password)
  }, [params, setGame, setName])

  useEffect(() => {
    if (user) fetchGame()
  }, [user, fetchGame])

  const handleSaveSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!game) return null
    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${game.id}/`,
      {
        method: "PUT",
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
      setGame(new Game(data))
      toast.success("Game saved")
      router.push(`/games/${game.id}`)
    } else {
      setErrors(data)
    }
  }

  const handleDeleteClick = async () => {
    const userConfirmed = window.confirm(
      `Are you sure you want to permanently delete this game?`,
    )
    if (!userConfirmed) return

    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${game!.id}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      },
    )
    if (response.ok) {
      toast.success("Game deleted")
      router.push("/games")
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
            { href: `/games/${game?.id}`, text: game?.name ?? "" },
            { text: "Edit" },
          ]}
        />
      </NavBar>
      {game && (
        <div className="flex flex-col gap-4 px-4 py-4 lg:px-10">
          <h2 className="text-xl">Edit game</h2>
          <form onSubmit={handleSaveSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <div className="flex items-baseline">
                <div className="min-w-[100px]">
                  <label htmlFor="username">Name:</label>
                </div>
                <input
                  id="username"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-[300px] rounded border border-neutral-600 p-1"
                />
              </div>
              {errors.name && (
                <label className="pl-[100px] text-sm text-red-600">
                  {errors.name}
                </label>
              )}
            </div>
            <div className="flex flex-col gap-1">
              <div className="flex items-baseline">
                <div className="min-w-[100px]">
                  <label htmlFor="username">Password:</label>
                </div>
                <input
                  id="username"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-[300px] rounded border border-neutral-600 p-1"
                />
              </div>
              {errors.password && (
                <label className="pl-[100px] text-sm text-red-600">
                  {errors.password}
                </label>
              )}
            </div>
            <div>
              <button
                type="submit"
                className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
              >
                Save changes
              </button>
            </div>
          </form>
          <div className="mt-10 flex flex-col items-start gap-2">
            <h3 className="text-xl">Delete game</h3>
            <button
              onClick={handleDeleteClick}
              className="rounded-md border border-red-600 px-4 py-1 text-red-600 hover:bg-red-100"
            >
              Permanently delete game
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default EditGamePage
