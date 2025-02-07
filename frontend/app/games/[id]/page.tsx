"use client"

import { useCallback, useEffect, useState } from "react"
import { useParams } from "next/navigation"
import useWebSocket from "react-use-websocket"

import Game, { GameData } from "@/classes/Game"
import { useAppContext } from "@/contexts/AppContext"
import Link from "next/link"
import Breadcrumb, { BreadcrumbItem } from "@/components/Breadcrumb"

const GamePage = () => {
  const { user } = useAppContext()
  const [game, setGame] = useState<Game | undefined>()

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
  }, [params, setGame])

  const {} = useWebSocket(
    `${process.env.NEXT_PUBLIC_BACKEND_WS_ORIGIN}/ws/games/${params.id}/`,
    {
      onOpen: () => {
        console.log("Game WebSocket connection opened")
      },

      onClose: async () => {
        console.log("Game WebSocket connection closed")
      },

      shouldReconnect: () => (user ? true : false),
    }
  )

  useEffect(() => {
    if (user) fetchGame()
  }, [user, fetchGame])

  if (!user) return null

  // Reduces breadcrumb flickering
  const getBreadcrumbItems = () => {
    const items: BreadcrumbItem[] = [
      { href: "/", text: "Home" },
      { href: "/games", text: "Games" },
    ]
    if (game) {
      items.push({ text: game.name })
    } else {
      items.push({ text: "" })
    }
    return items
  }

  return (
    <>
      <div className="px-6 pb-2">
        <Breadcrumb items={getBreadcrumbItems()} />
      </div>
      <hr className="border-neutral-300" />
      {game && (
        <div className="px-6 py-4 flex flex-col gap-4">
          <div>
            <p className="text-neutral-600">Game</p>
            <h1 className="text-xl">{game && game.name}</h1>
          </div>
          <p>
            <span className="inline-block w-[100px]">Host:</span>{" "}
            {user.username}
          </p>
          {game.host.id === user.id && (
            <div className="flex">
              <Link
                href={`/games/${game.id}/edit`}
                className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
              >
                Edit game
              </Link>
            </div>
          )}
        </div>
      )}
    </>
  )
}

export default GamePage
