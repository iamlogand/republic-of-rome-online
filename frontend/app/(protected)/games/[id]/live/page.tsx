"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import { DebouncedFunc, debounce } from "lodash"
import { useParams, useRouter } from "next/navigation"

import AvailableAction from "@/classes/AvailableAction"
import Campaign from "@/classes/Campaign"
import CombatCalculation, {
  CombatCalculationData,
} from "@/classes/CombatCalculation"
import EnemyLeader from "@/classes/EnemyLeader"
import Faction from "@/classes/Faction"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import ActionDispatcher from "@/components/ActionDispatcher"
import CombatCalculator from "@/components/CombatCalculator"
import GameEffects from "@/components/GameEffects"
import { ActionSelection } from "@/components/GenericActionForm"
import LogList from "@/components/LogList"
import SenatorDisplay from "@/components/SenatorDisplay"
import { useGameContext } from "@/contexts/GameContext"
import { cardLabel } from "@/helpers/cardLabel"
import { getDeployedForces } from "@/helpers/deploymentProposal"
import getDiceProbability from "@/helpers/dice"
import { forceListToString } from "@/helpers/forceLists"
import { getEvilOmensLevel } from "@/helpers/gameEffects"
import { STATESMAN_ABILITIES } from "@/helpers/statesmen"
import { toFamilyAdjective, toSentenceCase } from "@/helpers/text"

const LiveGamePage = () => {
  const {
    publicGameState,
    privateGameState,
    lastGameMessage,
    sendJsonMessage,
  } = useGameContext()
  const params = useParams()
  const router = useRouter()

  // Combat calculations — local state synced to other players via WebSocket
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

  // Action selection — local UI state, never leaves the browser
  const [selectionMap, setSelectionMap] = useState<
    Record<string, ActionSelection>
  >({})
  const [expandedActionId, setExpandedActionId] = useState<string | null>(null)
  const [actionResetKey, setActionResetKey] = useState(0)

  useEffect(() => {
    if (publicGameState?.game && publicGameState.game.status === "pending") {
      router.replace(`/games/${params.id}`)
    }
  }, [publicGameState, params.id, router])

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

  useEffect(() => {
    setSelectionMap({})
    setExpandedActionId(null)
    setActionResetKey((k) => k + 1)
  }, [publicGameState?.game?.phase])

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

  const handleActionSubmitSuccess = useCallback((id: string) => {
    setSelectionMap((prev) => ({ ...prev, [id]: {} }))
    setActionResetKey((k) => k + 1)
  }, [])

  const updateSelection = useCallback(
    (
      id: string | number,
      newSelection:
        | ActionSelection
        | ((prev: ActionSelection | undefined) => ActionSelection),
    ) => {
      setSelectionMap((prev) => ({
        ...prev,
        [id]:
          typeof newSelection === "function"
            ? newSelection(prev[id] ?? {})
            : newSelection,
      }))
    },
    [],
  )

  const handleTransferToProposal = useCallback(
    (calculation: CombatCalculation) => {
      if (!privateGameState || !publicGameState) return

      const deployed = getDeployedForces(
        publicGameState,
        calculation.commander,
        calculation.war,
      )

      const additionalRegularNeeded = Math.max(
        0,
        calculation.regularLegions - deployed.legions,
      )
      const additionalVeteransNeeded = Math.max(
        0,
        calculation.veteranLegions - deployed.veteranLegions,
      )
      const additionalFleetsNeeded = Math.max(
        0,
        calculation.fleets - deployed.fleets,
      )

      const availableRegularLegions = publicGameState.legions
        .filter(
          (l) => !l.veteran && l.campaign === null && l.allegiance === null,
        )
        .sort((a, b) => a.number - b.number)
        .slice(0, additionalRegularNeeded)
        .map((l) => l.id)

      const availableVeteranLegions = publicGameState.legions
        .filter(
          (l) => l.veteran && l.campaign === null && l.allegiance === null,
        )
        .sort((a, b) => a.number - b.number)
        .slice(0, additionalVeteransNeeded)
        .map((l) => l.id)

      const availableFleets = publicGameState.fleets
        .filter((f) => f.campaign === null)
        .sort((a, b) => a.number - b.number)
        .slice(0, additionalFleetsNeeded)
        .map((f) => f.id)

      const existingCampaign =
        calculation.commander !== null && calculation.war !== null
          ? publicGameState.campaigns.find(
              (c) =>
                c.commander === calculation.commander &&
                c.war === calculation.war,
            )
          : undefined

      if (existingCampaign) {
        const reinforceAction = privateGameState.availableActions.find(
          (action) => action.name === "Propose reinforcing proconsul",
        )
        if (!reinforceAction) return

        const newSelection: ActionSelection = {}
        newSelection["Campaign"] = existingCampaign.id
        if (calculation.regularLegions > 0 || calculation.veteranLegions > 0) {
          newSelection["Legions"] = [
            ...availableRegularLegions,
            ...availableVeteranLegions,
          ]
        }
        if (calculation.fleets > 0) {
          newSelection["Fleets"] = availableFleets
        }
        updateSelection(reinforceAction.identifier, newSelection)
        setExpandedActionId(reinforceAction.identifier)
        return
      }

      const deployAction = privateGameState.availableActions.find(
        (action) => action.name === "Propose deploying forces",
      )
      if (!deployAction) return

      const newSelection: ActionSelection = {}
      if (calculation.commander !== null) {
        newSelection["Commander"] = calculation.commander
      }
      if (calculation.war !== null) {
        newSelection["Target war"] = calculation.war
      }
      if (calculation.regularLegions > 0 || calculation.veteranLegions > 0) {
        newSelection["Legions"] = [
          ...availableRegularLegions,
          ...availableVeteranLegions,
        ]
      }
      if (calculation.fleets > 0) {
        newSelection["Fleets"] = availableFleets
      }
      updateSelection(deployAction.identifier, newSelection)
      setExpandedActionId(deployAction.identifier)
    },
    [privateGameState, publicGameState, updateSelection],
  )

  if (!publicGameState?.game) return null
  if (publicGameState.game.status === "pending") return null

  const game = publicGameState.game!
  const reserveLegions = publicGameState.legions.filter(
    (l) => l.campaign == null,
  )
  const reserveFleets = publicGameState.fleets.filter((f) => f.campaign == null)

  return (
    <div className="flex xl:flex">
      <div className="flex-1">
        <div>
          <div className="mt-4 flex flex-col">
            <div className="relative">
              <div className="flex w-full flex-col gap-4 px-4 pb-8 pt-4 lg:px-10">
                {publicGameState.game && (
                  <div className="mt-4 flex max-w-[1200px] flex-col gap-4 lg:grid lg:grid-cols-2">
                    <div className="flex flex-col gap-4">
                      <h3 className="text-xl">Sequence of play</h3>
                      <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2">
                        <div>Turn {game.turn}</div>
                        <div>
                          <span className="inline-block first-letter:uppercase">
                            {game.phase} phase
                          </span>
                        </div>
                        {game.status === "active" && (
                          <div>
                            {game.subPhase && (
                              <span className="inline-block items-center rounded-full bg-neutral-200 px-2 py-0.5 text-center text-sm text-neutral-600 first-letter:uppercase">
                                {game.subPhase}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                      <div>
                        {game.deckCount} card
                        {game.deckCount !== 1 && "s"} in the deck
                      </div>
                    </div>
                    <div className="flex flex-col gap-4">
                      <h3 className="text-xl">Rome</h3>
                      <div className="flex gap-4">
                        <div>State treasury: {game.stateTreasury}T</div>
                      </div>
                      <div className="flex flex-wrap gap-x-4">
                        <div>Unrest level: {game.unrest}</div>
                        <div>Famine severity: {game.famineSeverity}</div>
                        <div>Unprosecuted wars: {game.unprosecutedWars}</div>
                      </div>
                      {game.militaryCrisis && (
                        <div className="font-semibold text-red-600">
                          Military crisis
                        </div>
                      )}
                      <GameEffects effects={game.effects} />
                      <div>
                        Reserve forces:
                        {reserveLegions.length === 0 &&
                        reserveFleets.length === 0 ? (
                          " none"
                        ) : (
                          <ul>
                            {reserveLegions.length > 0 && (
                              <li className="ml-10 list-disc">
                                {reserveLegions.length}{" "}
                                {reserveLegions.length === 1
                                  ? "legion"
                                  : "legions"}{" "}
                                <span className="text-neutral-600">
                                  ({forceListToString(reserveLegions)})
                                </span>
                              </li>
                            )}
                            {reserveFleets.length > 0 && (
                              <li className="ml-10 list-disc">
                                {reserveFleets.length}{" "}
                                {reserveFleets.length === 1
                                  ? "fleet"
                                  : "fleets"}{" "}
                                <span className="text-neutral-600">
                                  ({forceListToString(reserveFleets)})
                                </span>
                              </li>
                            )}
                          </ul>
                        )}
                      </div>
                      {game.concessions.length > 0 && (
                        <div>
                          Unawarded concessions:
                          <ul>
                            {game.concessions.map((concession, index) => (
                              <li
                                key={index}
                                className="ml-10 list-disc first-letter:uppercase"
                              >
                                {concession}
                                {!game.availableConcessions.includes(
                                  concession,
                                ) && " (unavailable)"}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {publicGameState.senators.filter((s) => !s.alive).length >
                        0 && (
                        <div>
                          Families that may return to politics:
                          <ul>
                            {publicGameState.senators
                              .filter((s) => !s.alive)
                              .sort((a, b) =>
                                a.familyName.localeCompare(b.familyName),
                              )
                              .map((senator, index) => (
                                <li key={index} className="ml-10 list-disc">
                                  {toFamilyAdjective(senator.familyName)} family
                                </li>
                              ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <h3 className="mt-4 text-xl">Tools</h3>
                <div className="flex min-h-[34px] flex-wrap gap-x-4 gap-y-2">
                  <CombatCalculator
                    publicGameState={publicGameState as PublicGameState}
                    privateGameState={privateGameState}
                    combatCalculations={combatCalculations}
                    updateCombatCalculations={updateCombatCalculations}
                    onTransferToProposal={handleTransferToProposal}
                  />
                </div>

                {game.phase === "senate" && (
                  <>
                    <h3 className="mt-4 text-xl">Senate</h3>
                    <div className="flex flex-col gap-2">
                      <div>
                        Current proposal:{" "}
                        {game.currentProposal ? (
                          <b>{game.currentProposal}</b>
                        ) : (
                          <span className="text-neutral-600">None</span>
                        )}
                      </div>
                      {game.currentProposal && (
                        <div className="flex gap-4">
                          <span className="inline-block w-14">
                            Yea: {game.votesYea}
                          </span>
                          <span className="inline-block w-14">
                            Nay: {game.votesNay}
                          </span>
                          <span>Pending: {game.votesPending}</span>
                        </div>
                      )}
                      {game.defeatedProposals.length > 0 && (
                        <>
                          Defeated/vetoed proposals:
                          <ul>
                            {game.defeatedProposals.map((proposal, index) => (
                              <li key={index} className="ml-10 list-disc">
                                {proposal}
                              </li>
                            ))}
                          </ul>
                        </>
                      )}
                    </div>
                  </>
                )}

                <h3 className="mt-4 text-xl">Factions</h3>
                <div className="flex flex-col gap-4 2xl:grid 2xl:grid-cols-[repeat(auto-fill,minmax(700px,1fr))]">
                  {publicGameState.factions
                    .sort((a, b) => a.position - b.position)
                    .map((faction: Faction, index: number) => {
                      const senators = publicGameState.senators
                        .filter((s) => s.faction === faction.id && s.alive)
                        .sort((a, b) =>
                          a.familyName.localeCompare(b.familyName),
                        )
                      const myFaction =
                        privateGameState?.faction &&
                        privateGameState.faction.id === faction.id
                      const votes = senators
                        .filter((s) => s.location == "Rome")
                        .reduce((v, s) => v + s.votes, 0)
                      return (
                        <div
                          key={index}
                          className="relative rounded border border-neutral-400"
                        >
                          {myFaction && (
                            <div className="absolute inset-y-[-1px] left-[-1px] w-1 bg-[#630330]" />
                          )}
                          <div className="py-0.5">
                            <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2 py-2 pl-3 pr-4 text-[#630330] lg:pl-5 lg:pr-6">
                              <h4 className="text-xl font-semibold">
                                {faction.displayName}
                              </h4>
                              <div>{faction.player.username}</div>
                              {faction.statusItems.length > 0 &&
                                faction.statusItems.map(
                                  (status: string, index: number) => (
                                    <div
                                      key={index}
                                      className="flex items-center rounded-full bg-neutral-200 px-2 py-0.5 text-center text-sm text-neutral-600"
                                    >
                                      <span className="first-letter:uppercase">
                                        {status}
                                      </span>
                                    </div>
                                  ),
                                )}
                              {(votes > 0 || faction.cardCount > 0) && (
                                <div className="ml-auto flex items-baseline gap-x-4 text-neutral-600">
                                  {votes > 0 && (
                                    <div>
                                      <span className="text-lg">{votes}</span>{" "}
                                      <span className="text-sm">
                                        vote{votes !== 1 && "s"} in Rome
                                      </span>
                                    </div>
                                  )}
                                  {faction.cardCount > 0 && (
                                    <div>
                                      <span className="text-lg">
                                        {faction.cardCount}
                                      </span>{" "}
                                      <span className="text-sm">
                                        card{faction.cardCount !== 1 && "s"}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                            <div className="divide-y divide-neutral-300 border-t border-neutral-300">
                              {senators.map(
                                (senator: Senator, index: number) => (
                                  <SenatorDisplay
                                    key={index}
                                    senator={senator}
                                  />
                                ),
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                </div>

                {publicGameState.senators.some(
                  (s) => s.faction === null && s.alive,
                ) && (
                  <>
                    <h3 className="mt-4 text-xl">Unaligned senators</h3>
                    <div className="flex flex-col gap-4 2xl:grid 2xl:grid-cols-[repeat(auto-fill,minmax(700px,1fr))]">
                      <div className="rounded border border-neutral-400">
                        <div className="divide-y divide-neutral-300 py-0.5">
                          {publicGameState.senators
                            .filter((s) => s.faction === null && s.alive)
                            .sort((a, b) =>
                              a.familyName.localeCompare(b.familyName),
                            )
                            .map((senator: Senator, index: number) => (
                              <SenatorDisplay key={index} senator={senator} />
                            ))}
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {publicGameState.wars.length > 0 && (
                  <>
                    <h3 className="mt-4 text-xl">Wars</h3>
                    <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[repeat(auto-fill,minmax(400px,1fr))]">
                      {publicGameState.wars
                        .sort((a, b) => a.id - b.id)
                        .map((war: War, index: number) => {
                          const matchingWarMultiplier = war.seriesName
                            ? Math.max(
                                1,
                                publicGameState.wars.filter(
                                  (w) =>
                                    w.seriesName === war.seriesName &&
                                    w.status === "active",
                                ).length,
                              )
                            : 1
                          const leaderStrength = war.seriesName
                            ? publicGameState.enemyLeaders
                                .filter((l) => l.seriesName === war.seriesName)
                                .reduce((sum, l) => sum + l.strength, 0)
                            : 0
                          const effectiveLandStrength =
                            war.landStrength * matchingWarMultiplier +
                            leaderStrength
                          const effectiveNavalStrength =
                            war.navalStrength * matchingWarMultiplier +
                            leaderStrength
                          return (
                            <div
                              key={index}
                              className="flex flex-col gap-4 rounded border border-neutral-400 px-4 py-2 lg:px-6 lg:py-4"
                            >
                              <div className="flex w-full justify-between gap-4">
                                <div className="flex flex-col gap-2">
                                  <h4 className="text-lg font-semibold">
                                    {war.name}{" "}
                                    <span className="text-base font-normal text-neutral-600">
                                      in {war.location}
                                    </span>
                                  </h4>
                                  <div className="flex flex-wrap gap-x-2 gap-y-2">
                                    <div
                                      className={`flex items-center rounded-full px-2 py-0.5 text-center text-sm ${
                                        (war.status === "inactive" ||
                                          war.status === "defeated") &&
                                        "bg-neutral-200 text-neutral-600"
                                      } ${
                                        war.status === "active" &&
                                        "bg-red-100 text-red-600"
                                      } ${
                                        war.status === "imminent" &&
                                        "bg-amber-200 text-amber-900"
                                      }`}
                                    >
                                      <span className="first-letter:uppercase">
                                        {war.status}
                                      </span>
                                    </div>
                                    {war.unprosecuted && (
                                      <div className="flex items-center rounded-full bg-purple-100 px-2 py-0.5 text-center text-sm text-purple-600">
                                        Unprosecuted
                                      </div>
                                    )}
                                    {war.famine && (
                                      <div className="flex items-center rounded-full bg-purple-100 px-2 py-0.5 text-center text-sm text-purple-600">
                                        Famine severity +1
                                      </div>
                                    )}
                                    {war.navalStrength > 0 && (
                                      <div className="flex items-center rounded-full bg-neutral-200 px-2 py-0.5 text-center text-sm text-neutral-600">
                                        Undefeated navy
                                      </div>
                                    )}
                                  </div>
                                </div>
                                <div>
                                  <span className="text-sm/7 text-neutral-600">
                                    Spoils
                                  </span>{" "}
                                  {war.spoils}T
                                </div>
                              </div>
                              {(war.seriesName || war.famine) && (
                                <div className="flex flex-col gap-1">
                                  {war.seriesName && (
                                    <div>Series: {war.seriesName} Wars</div>
                                  )}
                                </div>
                              )}
                              <div className="grid grid-cols-2">
                                <div className="flex flex-col gap-1">
                                  <div>
                                    <span className="text-sm text-neutral-600">
                                      Land strength
                                    </span>{" "}
                                    {effectiveLandStrength}
                                  </div>
                                  {war.fleetSupport > 0 && (
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Fleet support
                                      </span>{" "}
                                      {war.fleetSupport}
                                    </div>
                                  )}
                                  {war.navalStrength > 0 && (
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Naval strength
                                      </span>{" "}
                                      {effectiveNavalStrength}
                                    </div>
                                  )}
                                </div>
                                <div className="flex flex-col gap-1">
                                  <div>
                                    <span className="text-sm text-neutral-600">
                                      Disaster chance
                                    </span>{" "}
                                    {(() => {
                                      let total = 0
                                      war.disasterNumbers.forEach((curr) => {
                                        total += getDiceProbability(3, 0, {
                                          exacts: [curr],
                                        })
                                      })
                                      return Math.round(total * 100)
                                    })()}
                                    %
                                  </div>
                                  <div>
                                    <span className="text-sm text-neutral-600">
                                      Standoff chance
                                    </span>{" "}
                                    {(() => {
                                      let total = 0
                                      war.standoffNumbers.forEach((curr) => {
                                        total += getDiceProbability(3, 0, {
                                          exacts: [curr],
                                        })
                                      })
                                      return Math.round(total * 100)
                                    })()}
                                    %
                                  </div>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                    </div>
                  </>
                )}

                {publicGameState.enemyLeaders.length > 0 && (
                  <>
                    <h3 className="mt-4 text-xl">Enemy Leaders</h3>
                    <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[repeat(auto-fill,minmax(400px,1fr))]">
                      {publicGameState.enemyLeaders
                        .sort((a, b) => a.id - b.id)
                        .map((leader: EnemyLeader, index: number) => (
                          <div
                            key={index}
                            className="flex gap-4 rounded border border-neutral-400 px-4 py-2 lg:px-6 lg:py-4"
                          >
                            <div className="flex grow flex-col items-start justify-between gap-4">
                              <div className="flex flex-col gap-2">
                                <h4 className="text-lg font-semibold">
                                  {leader.name}
                                </h4>
                                <div className="flex">
                                  <div
                                    className={`flex items-center rounded-full px-2 py-0.5 text-center text-sm ${
                                      leader.active
                                        ? "bg-red-100 text-red-600"
                                        : "bg-neutral-200 text-neutral-600"
                                    }`}
                                  >
                                    {leader.active ? "Active" : "Inactive"}
                                  </div>
                                </div>
                              </div>
                              <div>Series: {leader.seriesName} Wars</div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <div>
                                <span className="text-sm text-neutral-600">
                                  Strength
                                </span>{" "}
                                {leader.strength}
                              </div>
                              <div>
                                <span className="text-sm text-neutral-600">
                                  Disaster chance
                                </span>{" "}
                                {Math.round(
                                  getDiceProbability(3, 0, {
                                    exacts: [leader.disasterNumber],
                                  }) * 100,
                                )}
                                %
                              </div>
                              <div>
                                <span className="text-sm text-neutral-600">
                                  Standoff chance
                                </span>{" "}
                                {Math.round(
                                  getDiceProbability(3, 0, {
                                    exacts: [leader.standoffNumber],
                                  }) * 100,
                                )}
                                %
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  </>
                )}

                {publicGameState.campaigns.length > 0 && (
                  <>
                    <h3 className="mt-4 text-xl">Campaigns</h3>
                    <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[repeat(auto-fill,minmax(400px,1fr))]">
                      {publicGameState.campaigns
                        .sort((a, b) => a.id - b.id)
                        .map((campaign: Campaign, index: number) => {
                          const war = publicGameState.wars.find(
                            (w) => w.id === campaign.war,
                          )
                          if (!war) return

                          const commander = publicGameState.senators.find(
                            (s) => s.id === campaign.commander,
                          )
                          const masterOfHorse =
                            campaign.masterOfHorse !== null
                              ? publicGameState.senators.find(
                                  (s) => s.id === campaign.masterOfHorse,
                                )
                              : null
                          const legions = publicGameState.legions
                            .filter((l) => l.campaign === campaign.id)
                            .sort((a, b) => a.number - b.number)
                          const fleets = publicGameState.fleets
                            .filter((f) => f.campaign === campaign.id)
                            .sort((a, b) => a.number - b.number)

                          let recallReason = ""
                          if (!commander) {
                            recallReason = "lack of a commander"
                          } else if (war.navalStrength === 0) {
                            if (legions.length === 0) {
                              recallReason = "lack of legions"
                            } else if (fleets.length < war.fleetSupport) {
                              recallReason = "insufficient fleet support"
                            }
                          } else {
                            if (fleets.length == 0) {
                              recallReason = "lack of fleets"
                            }
                          }

                          return (
                            <div
                              key={index}
                              className="flex flex-col gap-4 rounded border border-neutral-400 px-4 py-2 lg:px-6 lg:py-4"
                            >
                              <div className="flex w-full items-baseline justify-between gap-4">
                                <h4 className="text-lg font-semibold">
                                  {toSentenceCase(campaign.displayName)}{" "}
                                  <span className="text-base font-normal text-neutral-600">
                                    in {war?.location}
                                  </span>
                                </h4>
                                <div className="text-nowrap">{war?.name}</div>
                              </div>
                              <div className="flex flex-col gap-1">
                                {masterOfHorse && (
                                  <p className="text-sm">
                                    Master of Horse: {masterOfHorse.displayName}
                                  </p>
                                )}
                                <p>
                                  {commander && (
                                    <span>
                                      The general{" "}
                                      {masterOfHorse ? (
                                        <span>
                                          and his Master of Horse{" "}
                                          {masterOfHorse.displayName}{" "}
                                          command{" "}
                                        </span>
                                      ) : (
                                        <span>commands </span>
                                      )}
                                    </span>
                                  )}
                                  {legions && legions.length > 0 && (
                                    <span>
                                      {legions.length}{" "}
                                      {legions.length > 1
                                        ? "legions"
                                        : "legion"}
                                      <> ({forceListToString(legions)})</>
                                    </span>
                                  )}
                                  {fleets &&
                                    fleets.length > 0 &&
                                    legions &&
                                    legions.length > 0 && <span> and </span>}
                                  {fleets && fleets.length > 0 && (
                                    <span>
                                      {fleets.length}{" "}
                                      {fleets.length > 1 ? "fleets" : "fleet"}
                                      <> ({forceListToString(fleets)})</>
                                    </span>
                                  )}
                                  {legions.length === 0 &&
                                    fleets.length === 0 && (
                                      <span>only a few loyal men</span>
                                    )}
                                </p>
                                {recallReason ? (
                                  <p className="text-sm text-red-600">
                                    Will be automatically recalled due to{" "}
                                    {recallReason}
                                  </p>
                                ) : (
                                  <p className="text-sm text-neutral-600">
                                    Preparing for a{" "}
                                    {war.navalStrength === 0 ? "land" : "naval"}{" "}
                                    battle
                                  </p>
                                )}
                              </div>
                            </div>
                          )
                        })}
                    </div>
                  </>
                )}

                {privateGameState?.faction && (
                  <>
                    <h3 className="mt-4 text-xl">
                      {privateGameState.faction.displayName} secrets
                    </h3>
                    <p>Faction treasury: {privateGameState.faction.treasury}</p>
                    <div>
                      Cards:{" "}
                      {privateGameState.faction.cards.length === 0 ? (
                        <span className="text-neutral-600">None</span>
                      ) : (
                        privateGameState.faction.cards.map(
                          (card: string, index: number) => (
                            <li
                              key={index}
                              className="ml-10 list-disc first-letter:uppercase"
                            >
                              {cardLabel(card)}
                              {card.startsWith("statesman:") &&
                                STATESMAN_ABILITIES[card.split(":")[1]] && (
                                  <span className="text-neutral-600">
                                    {" "}
                                    ({STATESMAN_ABILITIES[card.split(":")[1]]})
                                  </span>
                                )}
                            </li>
                          ),
                        )
                      )}
                    </div>
                  </>
                )}

                <div className="flex max-h-[450px] xl:hidden">
                  <LogList publicGameState={publicGameState as PublicGameState} />
                </div>
              </div>
              {privateGameState && !game.finishedOn && (
                <div className="bottom-0 w-full border-t border-neutral-300 bg-blue-50/75 px-4 pb-6 pt-4 backdrop-blur-sm xl:sticky xl:rounded-tr xl:border-r xl:px-10">
                  <div className="flex flex-col gap-4">
                    <h3 className="text-xl">Your available actions</h3>
                    <div className="flex min-h-[34px] flex-wrap gap-x-4 gap-y-2">
                      {privateGameState.availableActions.length > 0 ? (
                        privateGameState.availableActions
                          .sort((a, b) => a.position - b.position)
                          .map((availableAction: AvailableAction) => {
                            const id = availableAction.identifier
                            const currentSelection = selectionMap[id] ?? {}
                            return (
                              <ActionDispatcher
                                key={id}
                                availableAction={availableAction}
                                publicGameState={
                                  publicGameState as PublicGameState
                                }
                                privateGameState={privateGameState}
                                selection={currentSelection}
                                setSelection={(newSelection) =>
                                  updateSelection(id, newSelection)
                                }
                                isExpanded={expandedActionId === id}
                                setIsExpanded={(expanded) =>
                                  setExpandedActionId(expanded ? id : null)
                                }
                                resetKey={actionResetKey}
                                onSubmitSuccess={() =>
                                  handleActionSubmitSuccess(id)
                                }
                              />
                            )
                          })
                      ) : (
                        <p className="text-neutral-600">None right now</p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <div className="hidden xl:relative xl:block xl:w-[600px]">
        <div className="sticky top-0 h-[calc(100vh-40px)] w-full px-10">
          <div className="flex h-full flex-col py-8">
            <LogList publicGameState={publicGameState as PublicGameState} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default LiveGamePage
