"use client"

import Game from "@/classes/Game"
import { useAppContext } from "@/contexts/AppContext"
import { useEffect, useState } from "react"

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
      let games: Game[] = []
      responseData.forEach((item: any) => {
        if (
          Object.hasOwn(item, "id") &&
          (item.id ?? undefined !== undefined) &&
          Object.hasOwn(item, "name") &&
          (item.name ?? undefined !== undefined)
        ) {
          const game = new Game(item.id, item.name)
          games.push(game)
        }
      })
      setGames(games)
    }
    fetchGames()
  }, [user])

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
