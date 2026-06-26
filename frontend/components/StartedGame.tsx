"use client"

import { useEffect, useRef, useState } from "react"

import { DebouncedFunc, debounce } from "lodash"
import Link from "next/link"

import CombatCalculation, {
  CombatCalculationData,
} from "@/classes/CombatCalculation"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import GameContainer from "@/components/GameContainer"
import LogList from "@/components/LogList"
import { useAppContext } from "@/contexts/AppContext"
import { formatDate } from "@/helpers/date"
import { getEvilOmensLevel } from "@/helpers/gameEffects"

interface StartedGameProps {
  publicGameState: PublicGameState
  privateGameState: PrivateGameState | undefined
  lastGameMessage: MessageEvent<string> | null
  sendJsonMessage: (message: object) => void
}

const StartedGame = ({
  publicGameState,
  privateGameState,
  lastGameMessage,
  sendJsonMessage,
}: StartedGameProps) => {
  const { user } = useAppContext()
  const [metaVisible, setMetaVisible] = useState<boolean>(true)

  const [combatCalculations, setCombatCalculations] = useState<
    CombatCalculation[]
  >([])
  const [combatCalculationsTimestamp, setCombatCalculationsTimestamp] =
    useState<string>(new Date(Date.now() - 60000).toISOString())

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
        evil_omens: c.evilOmens,
        is_dictator: c.isDictator,
        master_of_horse: c.masterOfHorse,
      }))
      sendJsonMessage({ combat_calculations: calculationsJson, timestamp })
      setCombatCalculationsTimestamp(timestamp)
    }, 100)
  }

  useEffect(() => {
    return () => debouncedSendRef.current?.cancel()
  }, [])

  const calculationsMatch = (
    calc1: CombatCalculation,
    calc2: CombatCalculation,
  ): boolean =>
    calc1.commander === calc2.commander &&
    calc1.war === calc2.war &&
    calc1.battle === calc2.battle &&
    calc1.regularLegions === calc2.regularLegions &&
    calc1.veteranLegions === calc2.veteranLegions &&
    calc1.fleets === calc2.fleets

  useEffect(() => {
    const data = lastGameMessage?.data
    if (!data) return
    const parsedData = JSON.parse(data)
    if (!("combat_calculations" in parsedData)) return

    const timestamp = parsedData.timestamp
    if (timestamp < combatCalculationsTimestamp) return

    const incomingCalculations = parsedData.combat_calculations.map(
      (item: CombatCalculationData) => new CombatCalculation(item),
    )

    setCombatCalculations((prevCalculations) => {
      const result: CombatCalculation[] = []
      const matchedIncomingIds = new Set<number | "proposal" | null>()

      prevCalculations.forEach((localCalc) => {
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
              !matchedIncomingIds.has(c.id) && calculationsMatch(localCalc, c),
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

      incomingCalculations.forEach((incomingCalc: CombatCalculation) => {
        if (!matchedIncomingIds.has(incomingCalc.id)) {
          result.push(incomingCalc)
        }
      })

      return result
    })

    setCombatCalculationsTimestamp(timestamp)
  }, [lastGameMessage, combatCalculationsTimestamp])

  // Auto-switch naval calculations to land when a war's naval strength reaches 0.
  // Auto-clamp evil omens to the actual game level.
  useEffect(() => {
    if (!publicGameState) return
    const actualEvilOmensLevel = getEvilOmensLevel(
      publicGameState.game?.effects ?? [],
    )
    setCombatCalculations((prev) => {
      let changed = false
      const updated = prev.map((calc) => {
        let next = calc
        const war = publicGameState.wars.find((w) => w.id === calc.war)
        if (
          calc.battle === "naval" &&
          calc.war !== null &&
          war &&
          war.navalStrength === 0
        ) {
          changed = true
          next = new CombatCalculation({
            id: next.id as number | null,
            game: next.game,
            name: next.name,
            commander: next.commander,
            war: next.war,
            land_battle: true,
            regular_legions: next.regularLegions,
            veteran_legions: next.veteranLegions,
            fleets: next.fleets,
            evil_omens: next.evilOmens,
            auto_transformed: next.autoTransformed,
            is_dictator: next.isDictator,
            master_of_horse: next.masterOfHorse,
          })
        }
        if (next.evilOmens > actualEvilOmensLevel) {
          changed = true
          next = new CombatCalculation({
            id: next.id as number | null,
            game: next.game,
            name: next.name,
            commander: next.commander,
            war: next.war,
            land_battle: next.battle === "land",
            regular_legions: next.regularLegions,
            veteran_legions: next.veteranLegions,
            fleets: next.fleets,
            evil_omens: actualEvilOmensLevel,
            auto_transformed: next.autoTransformed,
            is_dictator: next.isDictator,
            master_of_horse: next.masterOfHorse,
          })
        }
        return next
      })
      if (changed) {
        latestCalculationsRef.current = updated
        updated.forEach((calc, i) => {
          if (calc !== prev[i]) {
            pendingUpdatesRef.current.set(calc.id, true)
          }
        })
        debouncedSendRef.current?.()
      }
      return changed ? updated : prev
    })
  }, [publicGameState])

  const updateCombatCalculations = (calculations: CombatCalculation[]) => {
    setCombatCalculations(calculations)
    latestCalculationsRef.current = calculations
    calculations.forEach((calc) => {
      pendingUpdatesRef.current.set(calc.id, true)
    })
    debouncedSendRef.current?.()
  }

  const game = publicGameState.game!

  return (
    <div className="flex xl:flex">
      <div className="flex-1">
        {metaVisible && (
          <div className="flex flex-col gap-4 border-b border-solid border-neutral-300 px-4 pb-8 pt-4 lg:px-10 xl:rounded-br xl:border-r">
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
                {game.startedOn && (
                  <li className="ml-10 list-disc">
                    Started on{" "}
                    {formatDate(game.startedOn, { showWeekday: true })}
                  </li>
                )}
                {game.finishedOn && (
                  <li className="ml-10 list-disc">
                    Finished on{" "}
                    {formatDate(game.finishedOn, { showWeekday: true })}
                  </li>
                )}
              </ul>
              <div className="mt-4 flex flex-col gap-x-4 gap-y-1 sm:flex-row">
                <p className="font-semibold">Factions</p>
                <ul className="flex flex-col">
                  {publicGameState.factions.map((faction) => (
                    <li
                      key={faction.id}
                      className="flex min-h-[28px] flex-wrap"
                    >
                      <span>Faction {faction.position}</span>
                      <span className="ml-4 inline-block">
                        {faction.player.username}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            {user && game.host.id === user.id && (
              <div className="flex">
                <Link
                  href={`/games/${game.id}/edit`}
                  className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100"
                >
                  Edit game
                </Link>
              </div>
            )}
          </div>
        )}
        <div className="relative h-0 overflow-visible">
          <div className="absolute top-0 z-50 flex px-8">
            <button
              className="rounded-b bg-blue-100 px-2 text-sm text-blue-600"
              onClick={() => setMetaVisible(!metaVisible)}
            >
              {metaVisible ? "Hide meta" : "Show meta"}
            </button>
          </div>
        </div>
        <GameContainer
          publicGameState={publicGameState}
          combatCalculations={combatCalculations}
          updateCombatCalculations={updateCombatCalculations}
          privateGameState={privateGameState}
        />
      </div>
      <div className="hidden xl:relative xl:block xl:w-[600px]">
        <div className="sticky top-0 h-[calc(100vh-40px)] w-full px-10">
          <div className="flex h-full flex-col py-8">
            <LogList publicGameState={publicGameState} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default StartedGame
