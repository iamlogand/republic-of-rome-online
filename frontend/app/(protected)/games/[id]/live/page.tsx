"use client"

import { useEffect } from "react"

import { useRouter } from "next/navigation"

import { useParams } from "next/navigation"

import StartedGame from "@/components/StartedGame"

import { useGameContext } from "@/contexts/GameContext"

const LiveGamePage = () => {
  const { publicGameState, privateGameState, lastGameMessage, sendJsonMessage } =
    useGameContext()
  const params = useParams()
  const router = useRouter()

  useEffect(() => {
    if (publicGameState?.game && publicGameState.game.status === "pending") {
      router.replace(`/games/${params.id}`)
    }
  }, [publicGameState, params.id, router])

  if (!publicGameState?.game) return null

  if (publicGameState.game.status === "pending") return null

  return (
    <StartedGame
      publicGameState={publicGameState}
      privateGameState={privateGameState}
      lastGameMessage={lastGameMessage}
      sendJsonMessage={sendJsonMessage}
    />
  )
}

export default LiveGamePage
