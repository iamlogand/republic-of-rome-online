"use client"

import Game, { GameData } from "@/classes/Game"
import Breadcrumb from "@/components/Breadcrumb"
import { useAppContext } from "@/contexts/AppContext"
import formatDate from "@/utils/date"
import Link from "next/link"
import { useEffect, useState } from "react"

const GamesPage = () => {
  const { user } = useAppContext()
  const [games, setGames] = useState<Game[]>([])

  const fetchGames = async () => {
    setGames([])
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/`,
      {
        credentials: "include",
      }
    )
    const data = await response.json()
    const fetchedGames: Game[] = []
    data.forEach((item: GameData) => {
      const game = new Game(item)
      fetchedGames.push(game)
    })
    setGames(fetchedGames)
  }

  useEffect(() => {
    if (user) fetchGames()
  }, [user, setGames])

  if (!user) return null

  return (
    <>
      <div className="px-6 pb-2">
        <Breadcrumb items={[{ href: "/", text: "Home" }, { text: "Games" }]} />
      </div>
      <hr className="border-neutral-300" />
      <div className="px-6 py-4 flex flex-col gap-4">
        <div className="flex gap-16 items-baseline">
          <h1 className="text-xl">Games</h1>
          <div className="flex gap-4">
            <button
              onClick={fetchGames}
              className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
            >
              Refresh list
            </button>
            <Link
              href="/games/new"
              className="px-2 py-1 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-100"
            >
              Create new game
            </Link>
          </div>
        </div>
        <div className="min-h-[400px] py-2 border border-neutral-300 rounded-lg overflow-auto">
          <table className="table-fixed border-separate border-spacing-x-4">
            <thead>
              <tr>
                <th className="w-[400px] text-start">Name</th>
                <th className="w-[200px] text-start">Host</th>
                <th className="w-[100px] text-start">Players</th>
                <th className="w-[300px] text-start">Created on</th>
              </tr>
            </thead>
            <tbody>
              {games.map((game: Game, index: number) => (
                <tr key={index}>
                  <td className="w-[400px] max-w-[400px]">
                    <Link href={`/games/${game.id}`}>
                      <div className="w-full hover:text-blue-600 text-ellipsis whitespace-nowrap overflow-hidden">
                        {game.name}
                      </div>
                    </Link>
                  </td>
                  <td className="w-[200px]">
                    <div className="text-ellipsis whitespace-nowrap overflow-hidden">
                      {game.host.username}
                    </div>
                  </td>
                  <td className="w-[100px]">
                    <div className="text-ellipsis whitespace-nowrap overflow-hidden">
                      {game.factions?.length}
                    </div>
                  </td>
                  <td className="w-[300px]">
                    <div className="text-ellipsis whitespace-nowrap overflow-hidden">
                      {formatDate(game.createdOn)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  )
}

export default GamesPage
