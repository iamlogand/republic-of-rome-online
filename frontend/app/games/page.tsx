"use client"

import Link from "next/link"
import { notFound } from "next/navigation"
import { useEffect, useState } from "react"

import Game, { GameData } from "@/classes/Game"
import Breadcrumb from "@/components/Breadcrumb"
import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"

const GamesPage = () => {
  const { user, loadingUser } = useAppContext()
  const [games, setGames] = useState<Game[]>([])

  const fetchGames = async () => {
    setGames([])
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/`,
      {
        credentials: "include",
      },
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

  if (!user) {
    if (loadingUser) return null
    notFound()
  }

  return (
    <>
      <NavBar visible>
        <Breadcrumb items={[{ href: "/", text: "Home" }, { text: "Games" }]} />
      </NavBar>
      <div className="flex flex-col gap-4 px-4 py-4 lg:px-10">
        <div className="flex flex-wrap items-baseline gap-x-16 gap-y-2">
          <h2 className="text-xl">Games</h2>
          <div className="flex flex-wrap gap-x-4 gap-y-2">
            <button
              onClick={fetchGames}
              className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
            >
              Refresh list
            </button>
            <Link
              href="/games/new"
              className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
            >
              Create new game
            </Link>
          </div>
        </div>
        <div className="min-h-[400px] overflow-auto rounded-lg border border-neutral-300 py-2">
          <table className="table-fixed border-separate border-spacing-x-4">
            <thead>
              <tr>
                <th className="w-[400px] text-start">Name</th>
                <th className="w-[200px] text-start">Host</th>
                <th className="w-[100px] text-center">Status</th>
                <th className="w-[100px] text-center">Players</th>
              </tr>
            </thead>
            <tbody>
              {games.map((game: Game, index: number) => (
                <tr key={index}>
                  <td className="w-[400px] max-w-[400px]">
                    <Link href={`/games/${game.id}`}>
                      <div className="w-full overflow-hidden text-ellipsis whitespace-nowrap hover:text-blue-600">
                        {game.name}
                      </div>
                    </Link>
                  </td>
                  <td className="w-[200px]">
                    <div className="overflow-hidden text-ellipsis whitespace-nowrap">
                      {game.host.username}
                    </div>
                  </td>
                  <td className="w-[100px]">
                    <div className="overflow-hidden text-ellipsis whitespace-nowrap text-center">
                      {game.status}
                    </div>
                  </td>
                  <td className="w-[100px]">
                    <div className="overflow-hidden text-ellipsis whitespace-nowrap text-center">
                      {game.factions?.length}
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
