"use client"

import { useEffect, useRef, useState } from "react"
import toast from "react-hot-toast"
import useWebSocket from "react-use-websocket"

import { DebouncedFunc, debounce } from "lodash"
import Link from "next/link"
import { notFound, useParams } from "next/navigation"

import CombatCalculation, {
  CombatCalculationData,
} from "@/classes/CombatCalculation"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import Breadcrumb from "@/components/Breadcrumb"
import GameContainer from "@/components/GameContainer"
import LogList from "@/components/LogList"
import NavBar from "@/components/NavBar"
import { useAppContext } from "@/contexts/AppContext"
import getCSRFToken from "@/utils/csrf"
import { formatDate } from "@/utils/date"

interface Error {
  detail?: string
  password?: string
}

const GamePage = () => {
  const { user, loadingUser } = useAppContext()
  const [publicGameState, setPublicGameState] = useState<
    PublicGameState | undefined
  >()
  const [combatCalculations, setCombatCalculations] = useState<
    CombatCalculation[]
  >([])
  const [combatCalculationsTimestamp, setCombatCalculationsTimestamp] =
    useState<string>(new Date(Date.now() - 60000).toISOString())
  const [privateGameState, setPrivateGameState] = useState<
    PrivateGameState | undefined
  >()
  const [metaVisible, setMetaVisible] = useState<boolean>(true)

  const params = useParams()

  const myFactionId = publicGameState?.factions.find(
    (f) => f.player.id === user?.id,
  )?.id

  const [visible, setVisible] = useState<boolean>(true)
  useEffect(() => {
    if (publicGameState?.game?.status !== "Active") {
      setVisible(true)
    }
  }, [publicGameState?.game?.status])

  // Game WebSocket connection

  const { sendJsonMessage, lastMessage: lastGameMessage } = useWebSocket(
    `${process.env.NEXT_PUBLIC_BACKEND_WS_ORIGIN}/ws/games/${params.id}/`,
    {
      onOpen: () => {
        console.log("Game WebSocket connection opened")
      },

      onClose: async () => {
        console.log("Game WebSocket connection closed")
      },

      shouldReconnect: () => !!user,
    },
  )

  const calculationsMatch = (
    calc1: CombatCalculation,
    calc2: CombatCalculation,
  ): boolean => {
    return (
      calc1.commander === calc2.commander &&
      calc1.war === calc2.war &&
      calc1.battle === calc2.battle &&
      calc1.regularLegions === calc2.regularLegions &&
      calc1.veteranLegions === calc2.veteranLegions &&
      calc1.fleets === calc2.fleets
    )
  }

  useEffect(() => {
    const data = lastGameMessage?.data
    if (data) {
      const parsedData = JSON.parse(data)
      Object.keys(parsedData).forEach((key) => {
        if (key === "public_game_state") {
          const state = new PublicGameState(parsedData[key])
          setPublicGameState(state)
          console.log(state)
        } else if (key === "combat_calculations") {
          const timestamp = parsedData["timestamp"]
          if (timestamp >= combatCalculationsTimestamp) {
            const incomingCalculations = parsedData[key].map(
              (item: CombatCalculationData) => new CombatCalculation(item),
            )
            setCombatCalculations((prevCalculations) => {
              const result: CombatCalculation[] = []
              const processedIds = new Set<number | "proposal" | null>()
              const matchedIncomingIds = new Set<number | "proposal" | null>()

              prevCalculations.forEach((localCalc) => {
                processedIds.add(localCalc.id)

                let incomingCalc = incomingCalculations.find(
                  (c: CombatCalculation) => c.id === localCalc.id,
                )
                if (
                  !incomingCalc &&
                  localCalc.id === null &&
                  pendingUpdatesRef.current.has(null)
                ) {
                  incomingCalc = incomingCalculations.find(
                    (c: CombatCalculation) =>
                      !matchedIncomingIds.has(c.id) &&
                      calculationsMatch(localCalc, c),
                  )
                  if (incomingCalc) {
                    matchedIncomingIds.add(incomingCalc.id)
                    pendingUpdatesRef.current.delete(null)
                    pendingUpdatesRef.current.set(incomingCalc.id, true)
                  }
                }
                if (incomingCalc) {
                  matchedIncomingIds.add(incomingCalc.id)
                }
                if (pendingUpdatesRef.current.has(localCalc.id)) {
                  if (
                    incomingCalc &&
                    (calculationsMatch(localCalc, incomingCalc) ||
                      incomingCalc.autoTransformed)
                  ) {
                    result.push(incomingCalc)
                    pendingUpdatesRef.current.delete(localCalc.id)
                  } else if (incomingCalc) {
                    result.push(localCalc)
                  }
                } else {
                  if (incomingCalc) {
                    result.push(incomingCalc)
                  }
                }
              })

              incomingCalculations.forEach(
                (incomingCalc: CombatCalculation) => {
                  if (!matchedIncomingIds.has(incomingCalc.id)) {
                    result.push(incomingCalc)
                  }
                },
              )

              return result
            })

            setCombatCalculationsTimestamp(timestamp)
          }
        }
      })
    }
  }, [lastGameMessage, combatCalculationsTimestamp])

  // Player WebSocket connection

  const [playerSocketUrl, setPlayerSocketUrl] = useState<string | null>(null)

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
    onOpen: () => {
      console.log("Player WebSocket connection opened")
    },
    onClose: async () => {
      console.log("Player WebSocket connection closed")
    },
    shouldReconnect: () => !!user,
  })

  useEffect(() => {
    const data = lastPlayerMessage?.data
    if (data) {
      const parsedData = JSON.parse(data)
      const state = new PrivateGameState(parsedData["private_game_state"])
      setPrivateGameState(state)
      console.log(state)
    }
  }, [lastPlayerMessage])

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

  // Update combat calculator

  const latestCalculationsRef = useRef<CombatCalculation[]>([])
  const pendingUpdatesRef = useRef<Map<number | "proposal" | null, boolean>>(
    new Map(),
  )
  const debouncedSendRef = useRef<DebouncedFunc<() => void> | null>(null)

  if (!debouncedSendRef.current) {
    debouncedSendRef.current = debounce(() => {
      const timestamp = new Date().toISOString()
      const calculationsJson = latestCalculationsRef.current.map((c) => ({
        id: c.id,
        game: c.game,
        name: c.name,
        commander: c.commander,
        war: c.war,
        land_battle: c.battle === "land",
        regular_legions: c.regularLegions,
        veteran_legions: c.veteranLegions,
        fleets: c.fleets,
      }))
      sendJsonMessage({
        combat_calculations: calculationsJson,
        timestamp,
      })
      setCombatCalculationsTimestamp(timestamp)
    }, 100)
  }

  useEffect(() => {
    return () => debouncedSendRef.current?.cancel()
  }, [])

  const updateCombatCalculations = (calculations: CombatCalculation[]) => {
    setCombatCalculations(calculations)
    latestCalculationsRef.current = calculations

    // Mark all modified calculations as having pending local changes
    calculations.forEach((calc) => {
      pendingUpdatesRef.current.set(calc.id, true)
    })

    debouncedSendRef.current?.()
  }

  // Joining and leaving

  const dialogRef = useRef<HTMLDialogElement>(null)
  const [joinPosition, setJoinPosition] = useState<number | null>(null)
  const [password, setPassword] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)
  const [errors, setErrors] = useState<Error>({})

  const handleOpenDialog = (position: number) => {
    setJoinPosition(position)
    dialogRef.current?.showModal()
  }

  const handleCloseDialog = () => {
    dialogRef.current?.close()
    setPassword("")
    setErrors({})
  }

  const handleJoinButtonClick = async (position: number) => {
    if (publicGameState?.game && user) {
      if (
        publicGameState.game.hasPassword &&
        publicGameState.game.host.id !== user.id
      ) {
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
        body: JSON.stringify({
          game: publicGameState!.game!.id,
          position: position,
          password: password,
        }),
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
      if (result) {
        setErrors(result)
      }
    }
  }

  const handleLeaveClick = async (factionId: number) => {
    setLoading(true)
    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/factions/${factionId}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      },
    )
    setLoading(false)
    if (response.ok) {
      toast.success("You've left this game")
    }
  }

  const handleStartClick = async () => {
    const userConfirmed = window.confirm(
      "Are you sure you want to start this game?",
    )
    if (!userConfirmed) return

    const csrfToken = getCSRFToken()
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${publicGameState?.game?.id}/start-game/`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      },
    )
    if (response.ok) {
      toast.success("Game started")
    }
  }

  if (!user) {
    if (loadingUser) return null
    notFound()
  }

  return (
    <>
      <NavBar
        visible={visible}
        setVisible={
          publicGameState?.game?.status === "Active" ? setVisible : undefined
        }
      >
        <div>
          <Breadcrumb
            items={[
              { href: "/", text: "Home" },
              { href: "/games", text: "Games" },
              { text: publicGameState?.game?.name ?? "" },
            ]}
          />
        </div>
      </NavBar>

      <div className="flex xl:flex">
        <div className="flex-1">
          {publicGameState?.game && (
            <>
              {metaVisible && (
                <div
                  className={`flex flex-col gap-4 border-solid border-neutral-300 px-4 pb-8 pt-4 lg:px-10 ${publicGameState?.game?.status === "Active" && "border-b xl:rounded-br xl:border-r"}`}
                >
                  <div className="flex flex-col gap-4">
                    <div className="mt-2 flex">
                      <div className="flex items-center rounded-full bg-neutral-200 px-2 text-center text-sm text-neutral-600">
                        {publicGameState.game.status} game
                      </div>
                    </div>
                    <h2 className="text-2xl font-semibold text-[#630330]">
                      {publicGameState.game && publicGameState.game.name}
                    </h2>
                  </div>
                  <div className="flex flex-col gap-1">
                    <p>Hosted by {publicGameState.game.host.username}</p>
                    <div className="flex flex-col gap-1 text-sm text-neutral-600">
                      <p>
                        Created{" "}
                        {formatDate(publicGameState.game.createdOn, {
                          showWeekday: true,
                        })}
                      </p>
                      {publicGameState.game.startedOn && (
                        <p>
                          Started on{" "}
                          {formatDate(publicGameState.game.startedOn, {
                            showWeekday: true,
                          })}
                        </p>
                      )}
                      {publicGameState.game.finishedOn && (
                        <p className="flex flex-col sm:flex-row">
                          <span className="inline-block w-[100px]">
                            Finished on:
                          </span>
                          {formatDate(publicGameState.game.finishedOn, {
                            showWeekday: true,
                          })}
                        </p>
                      )}
                    </div>
                    <div className="mt-4 flex flex-col gap-x-4 gap-y-1 sm:flex-row">
                      <p className="font-semibold">Factions</p>
                      <ul className="flex flex-col">
                        {[1, 2, 3, 4, 5, 6].map((position: number) => {
                          const faction = publicGameState.factions.find(
                            (f) => f.position === position,
                          )

                          if (
                            !faction &&
                            publicGameState.game?.status !== "Pending"
                          )
                            return null

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
                              {publicGameState.game?.status == "Pending" && (
                                <span className="ml-4 inline-block">
                                  {!faction && !myFactionId && (
                                    <>
                                      <button
                                        onClick={() =>
                                          handleJoinButtonClick(position)
                                        }
                                        className="rounded-md border border-blue-600 px-2 text-blue-600 hover:bg-blue-100"
                                        disabled={loading}
                                      >
                                        Join
                                      </button>
                                    </>
                                  )}
                                  {!faction && myFactionId && (
                                    <span className="text-neutral-600">
                                      Open
                                    </span>
                                  )}
                                  {faction && faction.id === myFactionId && (
                                    <button
                                      onClick={() =>
                                        handleLeaveClick(faction.id)
                                      }
                                      className="rounded-md border border-red-600 px-2 text-red-600 hover:bg-red-100"
                                      disabled={loading}
                                    >
                                      Leave
                                    </button>
                                  )}
                                </span>
                              )}
                            </li>
                          )
                        })}
                      </ul>
                    </div>
                  </div>
                  {publicGameState.game.host.id === user.id && (
                    <div className="flex flex-wrap gap-x-4 gap-y-2">
                      <div className="flex">
                        <Link
                          href={`/games/${publicGameState.game.id}/edit`}
                          className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
                        >
                          Edit game
                        </Link>
                      </div>
                      {publicGameState.game.status === "Pending" &&
                        publicGameState.factions.length >= 3 && (
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
                </div>
              )}
              {publicGameState?.game?.status === "Active" && (
                <>
                  <div className="relative h-0 overflow-visible">
                    <div className="absolute top-0 z-50 flex px-8">
                      {!metaVisible ? (
                        <button
                          className="rounded-b bg-blue-100 px-2 text-sm text-blue-600"
                          onClick={() => setMetaVisible(true)}
                        >
                          Show meta
                        </button>
                      ) : (
                        <button
                          className="rounded-b bg-blue-100 px-2 text-sm text-blue-600"
                          onClick={() => setMetaVisible(false)}
                        >
                          Hide meta
                        </button>
                      )}
                    </div>
                  </div>
                  <GameContainer
                    publicGameState={publicGameState}
                    combatCalculations={combatCalculations}
                    updateCombatCalculations={updateCombatCalculations}
                    privateGameState={privateGameState}
                  />
                </>
              )}
            </>
          )}
        </div>
        {publicGameState?.game?.status === "Active" && (
          <div className="hidden xl:relative xl:block xl:w-[600px]">
            <div className="sticky top-0 h-[calc(100vh-40px)] w-full px-10">
              <div className="flex h-full flex-col py-8">
                <LogList publicGameState={publicGameState} />
              </div>
            </div>
          </div>
        )}
      </div>
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
                type="password"
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
                className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:opacity-50"
                disabled={loading}
              >
                Join
              </button>
            </div>
          </div>
        </form>
      </dialog>
    </>
  )
}

export default GamePage
