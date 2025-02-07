"use client"

import { useCallback, useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"

import Game, { GameData } from "@/classes/Game"
import { useAppContext } from "@/contexts/AppContext"
import getCSRFToken from "@/utils/csrf"
import Breadcrumbs, { BreadcrumbItem } from "@/components/Breadcrumbs"
import toast from "react-hot-toast"

interface ResponseError {
  name?: string
}

const EditGamePage = () => {
  const router = useRouter()

  const { user } = useAppContext()
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
    const game = new Game(data.id, data.name, data.host, data.created_on)
    setGame(game)
    setNewName(game.name)
  }, [params, setGame, setNewName])

  useEffect(() => {
    if (user) fetchGame()
  }, [user, fetchGame])

  // if (!user || !game || user.id !== game.host.id) return null
  if (!user) return null

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
      setGame(new Game(data.id, data.name, data.host, data.created_on))
      toast.success("Game saved")
      router.push(`/games/${game.id}`)
    } else {
      setErrors(data)
      console.error(data)
      toast.error("Something went wrong")
    }
  }

  const handleDeleteClick = async () => {
    if (!game) return null
    const userConfirmed = window.confirm(
      `Are you sure you want to permanently delete this game?`
    )
    if (!userConfirmed) return

    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${game.id}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      }
    )
    const data = await response.json()
    if (response.ok) {
      toast.success("Game deleted")
      router.push("/games")
    } else {
      console.error(data)
      toast.error("Something went wrong")
    }
  }

  // Reduces breadcrumb flickering
  const getBreadcrumbsItems = () => {
    const items: BreadcrumbItem[] = [
      { href: "/", text: "Home" },
      { href: "/games", text: "Games" },
    ]
    if (game) {
      items.push({ href: `/games/${game.id}`, text: game.name })
      items.push({ text: "Edit" })
    } else {
      items.push({ text: "" })
    }
    return items
  }

  return (
    <>
      <div className="px-6 pb-2">
        <Breadcrumbs items={getBreadcrumbsItems()} />
      </div>
      <hr className="border-neutral-300" />
      {game && (
        <div className="px-6 py-4 flex flex-col gap-4">
          <h1 className="text-xl">Edit game</h1>
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
                  className="w-[300px] p-1 border border-neutral-600 rounded"
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
                className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
              >
                Save changes
              </button>
            </div>
          </form>
          <div className="mt-10 flex flex-col gap-2 items-start">
            <h2 className="text-xl">Delete game</h2>
            <button
              onClick={handleDeleteClick}
              className="px-2 py-1 text-red-600 border border-red-600 rounded-md hover:bg-red-100"
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
