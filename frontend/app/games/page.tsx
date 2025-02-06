"use client"

import Game from "@/classes/Game"
import { useAppContext } from "@/contexts/AppContext"
import { useEffect, useState } from "react"

interface GameData {
  id: number
  name: string
}

const GamePage = () => {
  const { user } = useAppContext()
  const [games, setGames] = useState<Game[]>([])

  const fetchGames = async () => {
    setGames([])
    const fetchGamesResponse = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/`,
      {
        credentials: "include",
      }
    )
    const responseData = await fetchGamesResponse.json()
    const fetchedGames: GameData[] = []
    responseData.forEach((item: GameData) => {
      const game = new Game(item.id, item.name)
      fetchedGames.push(game)
    })
    setGames(fetchedGames)
  }

  useEffect(() => {
    if (!user) return
    fetchGames()
  }, [user, setGames])

  if (!user) return null

  return (
    <div className="px-6 py-4 max-w-[800px]">
      <div className="pb-2 flex gap-8 items-baseline">
        <h1 className="text-xl font-bold">Games</h1>
        <button
          onClick={fetchGames}
          className="px-2 py-1 text-blue-700 border border-blue-700 rounded-md"
        >
          Refresh list
        </button>
      </div>
      <ul>
        {games.map((game: Game, index: number) => (
          <li key={index}>{game.name}</li>
        ))}
      </ul>
    </div>
  )
}

export default GamePage
