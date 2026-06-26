"use client"

import { useEffect, useState } from "react"
import useWebSocket from "react-use-websocket"

import { useParams } from "next/navigation"

import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import PendingGame from "@/components/PendingGame"
import StartedGame from "@/components/StartedGame"
import { useAppContext } from "@/contexts/AppContext"

const GamePage = () => {
  const { user } = useAppContext()
  const params = useParams()

  const [publicGameState, setPublicGameState] = useState<
    PublicGameState | undefined
  >()
  const [privateGameState, setPrivateGameState] = useState<
    PrivateGameState | undefined
  >()
  const [playerSocketUrl, setPlayerSocketUrl] = useState<string | null>(null)

  const { sendJsonMessage, lastMessage: lastGameMessage } = useWebSocket(
    `${process.env.NEXT_PUBLIC_BACKEND_WS_ORIGIN}/ws/games/${params.id}/`,
    {
      onOpen: () => console.log("Game WebSocket connection opened"),
      onClose: async () => console.log("Game WebSocket connection closed"),
      shouldReconnect: () => !!user,
    },
  )

  useEffect(() => {
    const data = lastGameMessage?.data
    if (!data) return
    const parsedData = JSON.parse(data)
    if ("public_game_state" in parsedData) {
      const state = new PublicGameState(parsedData.public_game_state)
      setPublicGameState(state)
      console.log(state)
    }
  }, [lastGameMessage])

  useEffect(() => {
    if (
      user &&
      publicGameState?.factions.some(
        (faction: Faction) => faction.player.id === user.id,
      )
    ) {
      setPlayerSocketUrl(
        `${process.env.NEXT_PUBLIC_BACKEND_WS_ORIGIN}/ws/games/${params.id}/player/`,
      )
    } else {
      setPlayerSocketUrl(null)
    }
  }, [user, publicGameState, params.id])

  const { lastMessage: lastPlayerMessage } = useWebSocket(playerSocketUrl, {
    onOpen: () => console.log("Player WebSocket connection opened"),
    onClose: async () => console.log("Player WebSocket connection closed"),
    shouldReconnect: () => !!user,
  })

  useEffect(() => {
    const data = lastPlayerMessage?.data
    if (!data) return
    const parsedData = JSON.parse(data)
    const state = new PrivateGameState(parsedData.private_game_state)
    setPrivateGameState(state)
    console.log(state)
  }, [lastPlayerMessage])

  if (!user) return null

  if (!publicGameState?.game) return null

  if (publicGameState.game.status === "pending")
    return <PendingGame publicGameState={publicGameState} />

  return (
    <StartedGame
      publicGameState={publicGameState}
      privateGameState={privateGameState}
      lastGameMessage={lastGameMessage}
      sendJsonMessage={sendJsonMessage}
    />
  )
}

export default GamePage
