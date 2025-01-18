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

  useEffect(() => {
    if (!user) return

    const fetchGames = async () => {
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
    fetchGames()
  }, [user, games, setGames])

  return (
    <div className="px-6 py-4 max-w-[800px]">
      {user ? (
        <>
          <h1>Games</h1>
          {games.length > 0 ? (
            <ul>
              {games.map((game: Game, index: number) => (
                <li key={index}>
                  {game.name} ({game.id})
                </li>
              ))}
            </ul>
          ) : (
            <p>No games</p>
          )}
        </>
      ) : (
        <p>Games are only visible to signed in users</p>
      )}
    </div>
  )
}

export default GamePage
