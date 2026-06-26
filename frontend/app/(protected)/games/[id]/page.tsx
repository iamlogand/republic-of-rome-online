"use client"

import { useEffect } from "react"

import { useRouter } from "next/navigation"
import { useParams } from "next/navigation"

import PendingGame from "@/components/PendingGame"
import { useGameContext } from "@/contexts/GameContext"

const GamePage = () => {
  const { publicGameState } = useGameContext()
  const params = useParams()
  const router = useRouter()

  useEffect(() => {
    if (publicGameState?.game && publicGameState.game.status !== "pending") {
      router.replace(`/games/${params.id}/live`)
    }
  }, [publicGameState, params.id, router])

  if (publicGameState?.game && publicGameState.game.status !== "pending") {
    return null
  }

  return <PendingGame publicGameState={publicGameState} />
}

export default GamePage
