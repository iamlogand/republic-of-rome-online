"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams, notFound } from "next/navigation"
import useWebSocket from "react-use-websocket"

import Breadcrumb from "@/components/Breadcrumb"
import PublicGameState from "@/classes/PublicGameState"
import PrivateGameState from "@/classes/PrivateGameState"
import { useAppContext } from "@/contexts/AppContext"
import { formatDate } from "@/utils/date"
import getCSRFToken from "@/utils/csrf"
import toast from "react-hot-toast"
import GameContainer from "@/components/GameContainer"
import Faction from "@/classes/Faction"
import LogList from "@/components/Logs"

const GamePage = () => {
  const { user, loadingUser } = useAppContext()
  const [publicGameState, setPublicGameState] = useState<
    PublicGameState | undefined
  >()
  const [privateGameState, setPrivateGameState] = useState<
    PrivateGameState | undefined
  >()

  const params = useParams()

  const myFactionId = publicGameState?.factions.find(
    (f) => f.player.id === user?.id
  )?.id

  const { lastMessage: lastGameMessage } = useWebSocket(
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
    const data = lastGameMessage?.data
    if (data) {
      const parsedData = JSON.parse(data)
      const state = new PublicGameState(parsedData)
      setPublicGameState(state)
      console.log(state)
    }
  }, [lastGameMessage])

  const [playerSocketUrl, setPlayerSocketUrl] = useState<string | null>(null)

  useEffect(() => {
    if (
      user &&
      publicGameState?.factions.some(
        (faction: Faction) => faction.player.id === user.id
      )
    ) {
      setPlayerSocketUrl(
        `${process.env.NEXT_PUBLIC_BACKEND_WS_ORIGIN}/ws/games/${params.id}/player/`
      )
    } else {
      setPlayerSocketUrl(null)
    }
  }, [user, publicGameState, params.id])

  const { lastMessage: lastPlayerMessage } = useWebSocket(playerSocketUrl, {
    onOpen: () => {
      console.log("Player WebSocket connection opened")
    },
    onClose: async () => {
      console.log("Player WebSocket connection closed")
    },
    shouldReconnect: () => (user ? true : false),
  })

  useEffect(() => {
    const data = lastPlayerMessage?.data
    if (data) {
      const parsedData = JSON.parse(data)
      const state = new PrivateGameState(parsedData)
      setPrivateGameState(state)
      console.log(state)
    }
  }, [lastPlayerMessage])

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
        body: JSON.stringify({
          game: publicGameState!.game!.id,
          position: position,
        }),
      }
    )
    if (response.ok) {
      toast.success("You've joined this game")
    }
  }

  const handleLeaveClick = async (factionId: number) => {
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

  const handleStartClick = async () => {
    const userConfirmed = window.confirm(
      `Are you sure you want to start this game?`
    )
    if (!userConfirmed) return

    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${publicGameState?.game?.id}/start-game/`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      }
    )
    if (response.ok) {
      toast.success("Game started")
    }
  }

  if (!user) {
    if (loadingUser) return null
    notFound()
  }

  return (
    <>
      <div>
        <div className="px-4 lg:px-10 pb-2">
          <Breadcrumb
            items={[
              { href: "/", text: "Home" },
              { href: "/games", text: "Games" },
              { text: publicGameState?.game?.name ?? "" },
            ]}
          />
        </div>
        <hr className="border-neutral-300" />
      </div>
      <div className="lg:flex">
        <div className="grow">
          {publicGameState?.game && (
            <div className="px-4 lg:px-10 py-4 flex flex-col gap-4 mb-4">
              <div className="flex flex-col gap-4">
                <div className="flex mt-2">
                  <div className="text-sm px-2 rounded-full bg-neutral-200 text-neutral-600 flex items-center text-center">
                    {publicGameState.game.status} game
                  </div>
                </div>
                <h2 className="text-2xl font-semibold text-[#630330]">
                  {publicGameState.game && publicGameState.game.name}
                </h2>
              </div>
              <div className="flex flex-col gap-1">
                <p>Hosted by {publicGameState.game.host.username}</p>
                <div className="flex flex-col gap-1 text-sm text-neutral-600">
                  <p>Created on {formatDate(publicGameState.game.createdOn)}</p>
                  {publicGameState.game.startedOn && (
                    <p>
                      Started on {formatDate(publicGameState.game.startedOn)}
                    </p>
                  )}
                  {publicGameState.game.finishedOn && (
                    <p className="flex flex-col sm:flex-row">
                      <span className="inline-block w-[100px]">
                        Finished on:
                      </span>
                      {formatDate(publicGameState.game.finishedOn)}
                    </p>
                  )}
                </div>
                <div className="mt-4 flex flex-col sm:flex-row gap-x-4 gap-y-1">
                  <p className="font-semibold">Factions</p>
                  <ul className="flex flex-col">
                    {[1, 2, 3, 4, 5, 6].map((position: number) => {
                      const faction = publicGameState.factions.find(
                        (f) => f.position === position
                      )

                      if (
                        !faction &&
                        publicGameState.game?.status !== "Pending"
                      )
                        return null

                      return (
                        <li
                          key={position}
                          className="min-h-[28px] flex flex-wrap"
                        >
                          <span>Faction {position}</span>
                          {faction && (
                            <span className="inline-block ml-4">
                              {faction.player.username}
                            </span>
                          )}
                          {publicGameState.game?.status == "Pending" && (
                            <span className="inline-block ml-4">
                              {!faction && !myFactionId && (
                                <button
                                  onClick={() => handleJoinClick(position)}
                                  className="px-2 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
                                >
                                  Join
                                </button>
                              )}
                              {!faction && myFactionId && (
                                <span className="text-neutral-600">Open</span>
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
                          )}
                        </li>
                      )
                    })}
                  </ul>
                </div>
              </div>
              {publicGameState.game.host.id === user.id && (
                <div className="flex gap-x-4 gap-y-2 flex-wrap">
                  <div className="flex">
                    <Link
                      href={`/games/${publicGameState.game.id}/edit`}
                      className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
                    >
                      Edit game
                    </Link>
                  </div>
                  {publicGameState.game.status === "Pending" &&
                    publicGameState.factions.length >= 3 && (
                      <div className="flex">
                        <button
                          onClick={handleStartClick}
                          className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
                        >
                          Start game
                        </button>
                      </div>
                    )}
                </div>
              )}
            </div>
          )}
          {publicGameState?.game?.status === "Active" && (
            <>
              <div className="flex flex-row">
                <hr className="grow border-neutral-300" />
                <hr className="border-none w-10 h-px bg-gradient-to-r from-neutral-300 to-transparent" />
              </div>
              <GameContainer
                publicGameState={publicGameState}
                privateGameState={privateGameState}
              />
            </>
          )}
        </div>
        {publicGameState?.game?.status === "Active" && (
          <div className="hidden lg:block relative max-w-[550px] bg-white">
            <div className="sticky top-0 px-10 w-full h-[calc(100vh-40px)]">
              <div className="py-4 h-full flex flex-col">
                <LogList publicGameState={publicGameState} />
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default GamePage
