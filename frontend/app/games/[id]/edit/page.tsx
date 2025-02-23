"use client"

import { useCallback, useEffect, useState } from "react"
import { notFound, useParams, useRouter } from "next/navigation"
import toast from "react-hot-toast"

import Game, { GameData } from "@/classes/Game"
import { useAppContext } from "@/contexts/AppContext"
import getCSRFToken from "@/utils/csrf"
import Breadcrumb from "@/components/Breadcrumb"

interface ResponseError {
  name?: string
}

const EditGamePage = () => {
  const router = useRouter()

  const { user, loadingUser } = useAppContext()
  const [game, setGame] = useState<Game | undefined>()
  const [newName, setNewName] = useState<string>("")
  const [errors, setErrors] = useState<ResponseError>({})

  const params = useParams()

  const fetchGame = useCallback(async () => {
    setGame(undefined)
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${params.id}`,
      {
        credentials: "include",
      }
    )
    const data: GameData = await response.json()
    const game = new Game(data)
    setGame(game)
    setNewName(game.name)
  }, [params, setGame, setNewName])

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
        body: JSON.stringify({ name: newName }),
      }
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
      `Are you sure you want to permanently delete this game?`
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
      }
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
      <div className="px-6 pb-2">
        <Breadcrumb
          items={[
            { href: "/", text: "Home" },
            { href: "/games", text: "Games" },
            { href: `/games/${game?.id}`, text: game?.name ?? "" },
            { text: "Edit" },
          ]}
        />
      </div>
      <hr className="border-neutral-300" />
      {game && (
        <div className="px-6 py-4 flex flex-col gap-4">
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
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-[300px] p-1 border border-neutral-500 rounded"
                />
              </div>
              {errors.name && (
                <label className="pl-[100px] text-sm text-red-600">
                  {errors.name}
                </label>
              )}
            </div>
            <div>
              <button
                type="submit"
                className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
              >
                Save changes
              </button>
            </div>
          </form>
          <div className="mt-10 flex flex-col gap-2 items-start">
            <h3 className="text-xl">Delete game</h3>
            <button
              onClick={handleDeleteClick}
              className="px-4 py-1 text-red-600 border border-red-600 rounded-md hover:bg-red-100"
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
