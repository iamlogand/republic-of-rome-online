"use client"

import { createContext, useContext } from "react"

import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"

interface GameContextValue {
  publicGameState: PublicGameState | undefined
  privateGameState: PrivateGameState | undefined
  lastGameMessage: MessageEvent<string> | null
  sendJsonMessage: (message: object) => void
}

export const GameContext = createContext<GameContextValue | null>(null)

export const useGameContext = () => {
  const context = useContext(GameContext)
  if (!context) throw new Error("useGameContext must be used within GameContext")
  return context
}
