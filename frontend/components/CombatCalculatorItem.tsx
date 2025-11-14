import { useCallback, useMemo } from "react"
import React from "react"

import CombatCalculation from "@/classes/CombatCalculation"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import getDiceProbability from "@/utils/dice"

interface CombatCalculatorItemProps {
  publicGameState: PublicGameState
  combatCalculation: CombatCalculation
  updateCombatCalculation: (combatCalculation: CombatCalculation) => void
  isReadOnly?: boolean
}

const CombatCalculatorItem = ({
  publicGameState,
  combatCalculation,
  updateCombatCalculation,
  isReadOnly = false,
}: CombatCalculatorItemProps) => {
  const commander = publicGameState.senators.find(
    (commander: Senator) => commander.id === combatCalculation.commander,
  )

  const setCommander = (commander: number | null) => {
    if (combatCalculation.commander !== commander) {
      updateCombatCalculation({ ...combatCalculation, commander: commander })
    }
  }

  const war = publicGameState.wars.find(
    (war: War) => war.id === combatCalculation.war,
  )

  const setWar = (war: number | null) => {
    if (combatCalculation.war !== war) {
      updateCombatCalculation({ ...combatCalculation, war: war })
    }
  }

  const setRegularLegions = (value: number) => {
    if (combatCalculation.regularLegions !== value) {
      updateCombatCalculation({ ...combatCalculation, regularLegions: value })
    }
  }

  const setVeteranLegions = (value: number) => {
    if (combatCalculation.veteranLegions !== value) {
      updateCombatCalculation({
        ...combatCalculation,
        veteranLegions: value,
      })
    }
  }

  const setFleets = (value: number) => {
    if (combatCalculation.fleets !== value) {
      updateCombatCalculation({ ...combatCalculation, fleets: value })
    }
  }

  const setBattle = useCallback(
    (value: "land" | "naval", currentCalculation: CombatCalculation) => {
      if (currentCalculation.battle !== value) {
        updateCombatCalculation({ ...currentCalculation, battle: value })
      }
    },
    [updateCombatCalculation],
  )

  let forceStrength =
    combatCalculation.battle === "land"
      ? combatCalculation.regularLegions + combatCalculation.veteranLegions * 2
      : combatCalculation.fleets
  forceStrength += Math.min(commander?.military ?? 0, forceStrength)
  const warStrength =
    (combatCalculation.battle === "land"
      ? war?.landStrength
      : war?.navalStrength) ?? 0
  const modifier = forceStrength - warStrength

  const victoryProbability = useMemo(
    () =>
      Math.round(
        getDiceProbability(
          3,
          modifier,
          {
            min: 14,
          },
          [...(war?.standoffNumbers ?? []), ...(war?.disasterNumbers ?? [])],
        ) * 100,
      ),
    [modifier, war?.standoffNumbers, war?.disasterNumbers],
  )

  const stalemateProbability = useMemo(
    () =>
      Math.round(
        getDiceProbability(
          3,
          modifier,
          {
            min: 8,
            max: 13,
          },
          [...(war?.standoffNumbers ?? []), ...(war?.disasterNumbers ?? [])],
        ) * 100,
      ),
    [modifier, war?.standoffNumbers, war?.disasterNumbers],
  )

  const defeatProbability = useMemo(
    () =>
      Math.round(
        getDiceProbability(
          3,
          modifier,
          {
            max: 7,
          },
          [...(war?.standoffNumbers ?? []), ...(war?.disasterNumbers ?? [])],
        ) * 100,
      ),
    [modifier, war?.standoffNumbers, war?.disasterNumbers],
  )

  const standoffProbability = useMemo(
    () =>
      Math.round(
        getDiceProbability(3, 0, {
          exacts: war?.standoffNumbers,
        }) * 100,
      ),
    [war?.standoffNumbers],
  )

  const disasterProbability = useMemo(
    () =>
      Math.round(
        getDiceProbability(3, 0, {
          exacts: war?.disasterNumbers,
        }) * 100,
      ),
    [war?.disasterNumbers],
  )

  const renderNumberField = (
    name: string,
    value: number,
    updateValue: (newValue: number) => void,
  ) => {
    const min = 0
    const max = 25
    return (
      <div className="flex max-w-[350px] flex-col gap-1">
        <label htmlFor={name} className="font-semibold">
          {name}
        </label>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                updateValue(Number(value) > max ? max : Number(value) - 1)
              }}
              disabled={Number(value) <= min || isReadOnly}
              className="relative h-6 min-w-6 rounded-full border border-red-500 text-red-500 hover:bg-red-100 disabled:border-neutral-400 disabled:text-neutral-400 disabled:hover:bg-transparent"
            >
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                &minus;
              </div>
            </button>
            <input
              id={name}
              type="number"
              min={min}
              max={max}
              value={value}
              onChange={(e) => updateValue(Number(e.target.value))}
              required
              disabled={isReadOnly}
              className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5 disabled:cursor-not-allowed disabled:bg-neutral-100"
            />
            <button
              type="button"
              onClick={() => {
                updateValue(Number(value) < min ? min : Number(value) + 1)
              }}
              disabled={Number(value) >= max || isReadOnly}
              className="relative h-6 min-w-6 rounded-full border border-green-500 text-green-500 hover:bg-green-100 disabled:border-neutral-400 disabled:text-neutral-400 disabled:hover:bg-transparent"
            >
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                +
              </div>
            </button>
          </div>
          <div className="flex w-full items-center justify-center">
            <button
              type="button"
              className={`w-10 cursor-default px-2 text-sm ${
                value !== min && "text-neutral-400"
              }`}
              onClick={() => updateValue(min)}
              disabled={isReadOnly}
            >
              {min}
            </button>

            <input
              type="range"
              min={min}
              max={max}
              value={value}
              onChange={(e) => updateValue(Number(e.target.value))}
              disabled={isReadOnly}
              className="w-full disabled:cursor-not-allowed"
            ></input>
            <button
              type="button"
              className={`w-10 cursor-default px-2 text-sm ${
                value !== max && "text-neutral-400"
              }`}
              onClick={() => updateValue(max)}
              disabled={isReadOnly}
            >
              {max}
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-12 py-6 md:flex-row">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-1">
          <label htmlFor="commander" className="font-semibold">
            Commander{" "}
            <span className="text-sm font-normal text-neutral-600">
              (military skill)
            </span>
          </label>
          <select
            id="commander"
            value={commander?.id ?? ""}
            onChange={(e) =>
              setCommander(
                e.target.value !== "" ? Number(e.target.value) : null,
              )
            }
            required
            disabled={isReadOnly}
            className="rounded-md border border-blue-600 p-1 disabled:cursor-not-allowed disabled:bg-neutral-100"
          >
            <option value="">-- select an option --</option>
            {publicGameState.senators?.map(
              (senator: Senator, index: number) => (
                <option key={index} value={senator.id}>
                  <>
                    {senator?.displayName} ({senator.military})
                  </>
                </option>
              ),
            )}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="war" className="font-semibold">
            Target war
          </label>
          <select
            id="war"
            value={war?.id ?? ""}
            onChange={(e) =>
              setWar(e.target.value !== "" ? Number(e.target.value) : null)
            }
            required
            disabled={isReadOnly}
            className="rounded-md border border-blue-600 p-1 disabled:cursor-not-allowed disabled:bg-neutral-100"
          >
            <option value="">-- select an option --</option>
            {publicGameState.wars?.map((war: War, index: number) => (
              <option key={index} value={war.id}>
                <>{war?.name}</>
              </option>
            ))}
          </select>
        </div>
        <div className="flex gap-2">
          {war?.navalStrength !== 0 && (
            <button
              className={`select-none rounded-md border px-4 py-1 ${
                combatCalculation.battle === "naval"
                  ? "border-blue-600 bg-blue-200 text-blue-900"
                  : "border-neutral-400 text-neutral-500 hover:bg-neutral-100 disabled:hover:bg-transparent"
              }`}
              onClick={() => setBattle("naval", combatCalculation)}
              disabled={combatCalculation.battle === "naval" || isReadOnly}
            >
              Naval battle
            </button>
          )}
          <button
            className={`select-none rounded-md border px-4 py-1 ${
              combatCalculation.battle === "land"
                ? "border-green-600 bg-green-200 text-green-900"
                : "border-neutral-400 text-neutral-500 hover:bg-neutral-100 disabled:hover:bg-transparent"
            }`}
            onClick={() => setBattle("land", combatCalculation)}
            disabled={combatCalculation.battle === "land" || isReadOnly}
          >
            Land battle
          </button>
        </div>
        {renderNumberField(
          "Regular legions",
          combatCalculation.regularLegions,
          setRegularLegions,
        )}
        {renderNumberField(
          "Veteran legions",
          combatCalculation.veteranLegions,
          setVeteranLegions,
        )}
        {renderNumberField("Fleets", combatCalculation.fleets, setFleets)}
      </div>
      <div className="flex max-w-[350px] flex-col items-start gap-6">
        <div className="flex flex-col items-start gap-1">
          <div className="font-semibold">Strengths</div>
          <div>Roman force strength: {forceStrength}</div>
          {warStrength > 0 && <div>War strength: {warStrength}</div>}
        </div>
        {warStrength > 0 && (
          <div className="flex flex-col items-start gap-1">
            <div className="font-semibold">Probabilities</div>
            <div className="flex gap-1">
              <div className="flex min-w-[135px] flex-col items-start gap-2">
                <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                  Victory: {victoryProbability}%
                </div>
                <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                  Stalemate: {stalemateProbability}%
                </div>
                <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                  Defeat: {defeatProbability}%
                </div>
              </div>
              <div className="flex min-w-[135px] flex-col items-start gap-2">
                <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                  Disaster: {disasterProbability}%
                </div>
                <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                  Standoff: {standoffProbability}%
                </div>
              </div>
            </div>
          </div>
        )}
        {((combatCalculation.battle === "land" &&
          (war?.fleetSupport ?? 0) > combatCalculation.fleets) ||
          modifier < 0) && (
          <div className="flex flex-col gap-1">
            <div className="font-semibold">Issues</div>
            <div className="flex flex-col gap-2 text-sm">
              {combatCalculation.battle === "land" &&
                (war?.fleetSupport ?? 0) > combatCalculation.fleets && (
                  <>
                    <div className="rounded-md bg-red-50 px-2 py-1 text-red-600">
                      <strong className="font-semibold">
                        Insufficient fleet support
                      </strong>
                      : a minimum of {war?.fleetSupport} fleets are required to
                      prosecute this war
                    </div>
                  </>
                )}
              {modifier < 0 && (
                <>
                  <div className="rounded-md bg-red-50 px-2 py-1 text-red-600">
                    <strong className="font-semibold">
                      Below minimum force
                    </strong>
                    : commander consent required to deploy a force below the war
                    strength
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CombatCalculatorItem
