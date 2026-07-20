"use client"

import { useEffect, useRef, useState } from "react"
import toast from "react-hot-toast"

import Link from "next/link"
import { useParams, useRouter } from "next/navigation"

import Breadcrumb from "@/components/Breadcrumb"
import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"
import { useGameContext } from "@/contexts/GameContext"
import getCSRFToken from "@/helpers/csrf"
import { formatDate } from "@/helpers/date"

interface JoinError {
  detail?: string
  password?: string
}

const GamePage = () => {
  const { publicGameState } = useGameContext()
  const { user } = useAppContext()
  const params = useParams()
  const router = useRouter()
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [joinPosition, setJoinPosition] = useState<number | null>(null)
  const [password, setPassword] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)
  const [errors, setErrors] = useState<JoinError>({})
  const [devPresets, setDevPresets] = useState<
    { name: string; label: string }[]
  >([])
  const [selectedPreset, setSelectedPreset] = useState("")
  const [loadingPreset, setLoadingPreset] = useState<string | null>(null)

  useEffect(() => {
    if (publicGameState?.game && publicGameState.game.status !== "pending") {
      router.replace(`/games/${params.id}/live`)
    }
  }, [publicGameState, params.id, router])

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/test/presets/`, {
      credentials: "include",
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data?.presets) setDevPresets(data.presets)
      })
      .catch(() => {})
  }, [])

  if (publicGameState?.game && publicGameState.game.status !== "pending") {
    return null
  }

  const game = publicGameState?.game

  const myFactionId = publicGameState?.factions.find(
    (f) => f.player.id === user?.id,
  )?.id

  const handleOpenDialog = (position: number) => {
    setJoinPosition(position)
    dialogRef.current?.showModal()
  }

  const handleCloseDialog = () => {
    dialogRef.current?.close()
    setPassword("")
    setErrors({})
  }

  const performJoin = async (position: number) => {
    setLoading(true)
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
        body: JSON.stringify({ game: game?.id, position, password }),
      },
    )
    setLoading(false)
    if (response.ok) {
      setPassword("")
      setErrors({})
      handleCloseDialog()
      toast.success("You've joined this game")
    } else {
      const result = await response.json()
      if (result) setErrors(result)
    }
  }

  const handleJoinButtonClick = async (position: number) => {
    if (user && game) {
      if (game.hasPassword && game.host.id !== user.id) {
        handleOpenDialog(position)
      } else {
        performJoin(position)
      }
    }
  }

  const handleJoinFormSubmit = async (
    e: React.SyntheticEvent<HTMLFormElement>,
  ) => {
    e.preventDefault()
    if (joinPosition) performJoin(joinPosition)
  }

  const handleLeaveClick = async (factionId: number) => {
    setLoading(true)
    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/factions/${factionId}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: { "X-CSRFToken": csrfToken },
      },
    )
    setLoading(false)
    if (response.ok) toast.success("You've left this game")
  }

  const handleLoadPreset = async (preset: string) => {
    setLoadingPreset(preset)
    await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/test/load-preset/${game?.id}/`,
      {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ preset }),
      },
    )
    setLoadingPreset(null)
  }

  const handleStartClick = async () => {
    const userConfirmed = window.confirm(
      "Are you sure you want to start this game?",
    )
    if (!userConfirmed) return

    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${game?.id}/start-game/`,
      {
        method: "POST",
        credentials: "include",
        headers: { "X-CSRFToken": csrfToken },
      },
    )
    if (response.ok) toast.success("Game started")
  }

  return (
    <div className="flex min-h-screen flex-col items-center">
      <div className="flex w-full max-w-[1000px] flex-1 flex-col">
        <NavBar visible>
          <Breadcrumb
            items={[
              { href: "/", text: "Home" },
              { href: "/games", text: "Games" },
              { text: game?.name ?? "" },
            ]}
          />
        </NavBar>
        {game && (
          <div className="flex flex-col gap-4 px-4 pb-8 pt-4 lg:px-10">
            <div className="flex flex-col gap-4">
              <div className="mt-2 flex">
                <div className="rounded-full bg-neutral-200 px-2 text-center text-sm text-neutral-600 first-letter:uppercase">
                  {game.status} game
                </div>
              </div>
              <h2 className="text-2xl font-semibold text-[#630330]">
                {game.name}
              </h2>
            </div>
            <div className="flex flex-col gap-1">
              <p>Hosted by {game.host.username}</p>
              <ul className="flex flex-col gap-1 text-sm text-neutral-600">
                <li className="ml-10 list-disc">
                  Created on {formatDate(game.createdOn, { showWeekday: true })}
                </li>
              </ul>
              <div className="mt-4 flex flex-col gap-x-4 gap-y-1 sm:flex-row">
                <p className="font-semibold">Factions</p>
                <ul className="flex flex-col">
                  {[1, 2, 3, 4, 5, 6].map((position: number) => {
                    const faction = publicGameState.factions.find(
                      (f) => f.position === position,
                    )
                    return (
                      <li
                        key={position}
                        className="flex min-h-[28px] flex-wrap"
                      >
                        <span>Faction {position}</span>
                        {faction && (
                          <span className="ml-4 inline-block">
                            {faction.player.username}
                          </span>
                        )}
                        <span className="ml-4 inline-block">
                          {!faction && !myFactionId && (
                            <button
                              onClick={() => handleJoinButtonClick(position)}
                              className="rounded-md border border-blue-600 px-2 text-blue-600 hover:bg-blue-100"
                              disabled={loading}
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
                              className="rounded-md border border-red-600 px-2 text-red-600 hover:bg-red-100"
                              disabled={loading}
                            >
                              Leave
                            </button>
                          )}
                        </span>
                      </li>
                    )
                  })}
                </ul>
              </div>
            </div>
            {user && game.host.id === user.id && (
              <div className="flex flex-wrap gap-x-4 gap-y-2">
                <div className="flex">
                  <Link
                    href={`/games/${game.id}/edit`}
                    className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
                  >
                    Edit game
                  </Link>
                </div>
                {publicGameState.factions.length >= 3 && (
                  <div className="flex">
                    <button
                      onClick={handleStartClick}
                      className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
                    >
                      Start game
                    </button>
                  </div>
                )}
              </div>
            )}
            {devPresets.length > 0 &&
              user &&
              game.host.id === user.id &&
              publicGameState.factions.length >= 3 && (
                <div className="flex flex-col gap-2 pt-4">
                  <p className="text-sm text-neutral-500">Load preset</p>
                  <div className="flex items-center gap-2">
                    <select
                      value={selectedPreset}
                      onChange={(e) => setSelectedPreset(e.target.value)}
                      className="rounded-md border border-neutral-400 px-2 py-1 text-neutral-600"
                    >
                      <option value="" disabled>
                        Select preset
                      </option>
                      {devPresets.map(({ name, label }) => (
                        <option key={name} value={name}>
                          {label}
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={() => {
                        if (selectedPreset) handleLoadPreset(selectedPreset)
                      }}
                      disabled={!selectedPreset || loadingPreset !== null}
                      className="rounded-md border border-neutral-400 px-4 py-1 text-neutral-600 hover:bg-neutral-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                    >
                      {loadingPreset !== null ? "Loading…" : "Load"}
                    </button>
                  </div>
                </div>
              )}
          </div>
        )}
        <dialog
          ref={dialogRef}
          className="rounded-lg bg-white p-6 shadow-lg"
          onClose={handleCloseDialog}
        >
          <form onSubmit={handleJoinFormSubmit} className="flex flex-col gap-6">
            <div className="flex max-w-[400px] flex-col gap-4">
              <h3 className="text-xl">Join as Faction {joinPosition}</h3>
              <p>A password is required to join this game</p>
            </div>
            <div className="flex flex-col gap-4">
              {errors.detail && (
                <div className="text-sm text-red-600">
                  <p>{errors.detail}</p>
                </div>
              )}
              <div className="flex grow flex-col gap-1">
                <label htmlFor="password" className="font-semibold">
                  Password
                </label>
                <input
                  id="password"
                  type="text"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="off"
                  className="w-full rounded-md border border-blue-600 p-1 px-1.5"
                />
                {errors.password && (
                  <label className="text-sm text-red-600">
                    {errors.password}
                  </label>
                )}
              </div>
              <div className="mt-4 flex justify-end gap-4">
                <button
                  type="button"
                  onClick={handleCloseDialog}
                  className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                  disabled={loading}
                >
                  Join
                </button>
              </div>
            </div>
          </form>
        </dialog>
      </div>
    </div>
  )
}

export default GamePage
