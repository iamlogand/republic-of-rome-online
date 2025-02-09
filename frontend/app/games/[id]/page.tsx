"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import useWebSocket, { ReadyState } from "react-use-websocket"

import Breadcrumb from "@/components/Breadcrumb"
import GameState from "@/classes/GameState"
import { useAppContext } from "@/contexts/AppContext"
import formatDate from "@/utils/date"
import getCSRFToken from "@/utils/csrf"
import toast from "react-hot-toast"

const GamePage = () => {
  const { user } = useAppContext()
  const [gameState, setGameState] = useState<GameState | undefined>()

  const params = useParams()

  const myFactionId = gameState?.factions.find(
    (f) => f.player.id === user?.id
  )?.id

  const { lastMessage, readyState } = useWebSocket(
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
    const data = lastMessage?.data
    if (data) {
      const parsedData = JSON.parse(data)
      const gameState = new GameState(parsedData)
      setGameState(gameState)
    }
  }, [lastMessage])

  const handleJoinClick = async (position: number) => {
    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/factions/`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ game: gameState!.game!.id, position: position }),
      }
    )
    if (response.ok) {
      toast.success("You've joined this game")
    }
  }

  const handleLeaveClick = async (factionId: number) => {
    const userConfirmed = window.confirm(
      "Are you sure you want to leave this game?"
    )
    if (!userConfirmed) return

    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/factions/${factionId}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      }
    )
    if (response.ok) {
      toast.success("You've left this game")
    }
  }

  if (!user) return null

  return (
    <>
      <div className="px-6 pb-2">
        <Breadcrumb
          items={[
            { href: "/", text: "Home" },
            { href: "/games", text: "Games" },
            { text: gameState?.game?.name ?? "" },
          ]}
        />
      </div>
      <hr className="border-neutral-300" />
      {gameState?.game && (
        <div className="px-6 py-4 flex flex-col gap-4">
          <div>
            <p className="text-neutral-600">Game</p>
            <h1 className="text-xl">{gameState.game && gameState.game.name}</h1>
          </div>
          <div>
            {readyState == ReadyState.OPEN ? (
              <span className="px-2 py-1 rounded-full bg-green-600 text-white text-sm">
                Connected
              </span>
            ) : (
              <span className="px-2 py-1 rounded-full bg-red-600 text-white text-sm">
                Disconnected
              </span>
            )}
          </div>
          <div>
            <p>
              <span className="inline-block w-[100px]">Host:</span>
              {gameState.game.host.username}
            </p>
            <p>
              <span className="inline-block w-[100px]">Created on:</span>
              {formatDate(gameState.game.createdOn)}
            </p>
            <div className="flex mt-4">
              <p>
                <span className="inline-block w-[100px]">Factions:</span>
              </p>
              <ul className="flex flex-col gap-1">
                {[1, 2, 3, 4, 5, 6].map((position: number) => {
                  const faction = gameState.factions.find(
                    (f) => f.position === position
                  )

                  return (
                    <li key={position}>
                      <span>Faction {position}</span>
                      {faction && (
                        <span className="inline-block ml-4">
                          {faction.player.username}
                        </span>
                      )}
                      <span className="inline-block ml-4">
                        {!faction && !myFactionId && (
                          <button
                            onClick={() => handleJoinClick(position)}
                            className="px-2 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
                          >
                            Join
                          </button>
                        )}
                        {faction && faction.id === myFactionId && (
                          <button
                            onClick={() => handleLeaveClick(faction.id)}
                            className="px-2 text-red-600 border border-red-600 rounded-md hover:bg-red-100"
                          >
                            Leave
                          </button>
                        )}
                      </span>
                    </li>
                  )
                })}
              </ul>
            </div>
          </div>
          {gameState.game.host.id === user.id && (
            <div className="flex">
              <Link
                href={`/games/${gameState.game.id}/edit`}
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
