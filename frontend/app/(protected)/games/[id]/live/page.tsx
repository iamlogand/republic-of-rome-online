"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import { DebouncedFunc, debounce } from "lodash"
import { useParams, useRouter } from "next/navigation"

import CombatCalculation, {
  CombatCalculationData,
} from "@/classes/CombatCalculation"
import PublicGameState from "@/classes/PublicGameState"
import { ActionSelection } from "@/components/GenericActionForm"
import { useGameContext } from "@/contexts/GameContext"
import { getDeployedForces } from "@/helpers/deploymentProposal"
import { getEvilOmensLevel } from "@/helpers/gameEffects"

import ActionDispatcher from "@/components/ActionDispatcher"
import CombatCalculator, {
  CombatCalculatorHandle,
} from "@/components/CombatCalculator"
import GameMain from "@/components/GameMain"
import GameBar from "@/components/GameBar"
import LogList from "@/components/LogList"

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

  const combatCalculatorRef = useRef<CombatCalculatorHandle>(null)

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
        .filter((l) => !l.veteran && l.campaign === null && l.allegiance === null)
        .sort((a, b) => a.number - b.number)
        .slice(0, additionalRegularNeeded)
        .map((l) => l.id)

      const availableVeteranLegions = publicGameState.legions
        .filter((l) => l.veteran && l.campaign === null && l.allegiance === null)
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

  const game = publicGameState.game

  return (
    <>
      <div className="flex h-screen items-center justify-center xl:hidden">
        <p className="m-2 text-center text-neutral-600">
          This page requires a larger screen to display correctly
        </p>
      </div>
      <div className="hidden h-screen flex-col overflow-hidden xl:flex">
        <GameBar
          publicGameState={publicGameState as PublicGameState}
          privateGameState={privateGameState}
          onCombatCalculatorOpen={() => combatCalculatorRef.current?.open()}
        />
        <CombatCalculator
          ref={combatCalculatorRef}
          publicGameState={publicGameState as PublicGameState}
          privateGameState={privateGameState}
          combatCalculations={combatCalculations}
          updateCombatCalculations={updateCombatCalculations}
          onTransferToProposal={handleTransferToProposal}
        />
        <div className="flex flex-1 overflow-hidden border-t border-neutral-300">
          <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
            <GameMain
              publicGameState={publicGameState as PublicGameState}
              privateGameState={privateGameState}
            />
            {privateGameState && !game.finishedOn && (
              <ActionDispatcher
                privateGameState={privateGameState}
                publicGameState={publicGameState as PublicGameState}
                selectionMap={selectionMap}
                updateSelection={updateSelection}
                expandedActionId={expandedActionId}
                setExpandedActionId={setExpandedActionId}
                actionResetKey={actionResetKey}
                onSubmitSuccess={handleActionSubmitSuccess}
              />
            )}
          </div>
          <LogList publicGameState={publicGameState as PublicGameState} />
        </div>
      </div>
    </>
  )
}

export default LiveGamePage
