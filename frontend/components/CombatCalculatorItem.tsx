import { useCallback } from "react"

import CombatCalculation from "@/classes/CombatCalculation"
import EnemyLeader from "@/classes/EnemyLeader"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import getDiceProbability from "@/helpers/dice"
import { SERIES_NULLIFIERS } from "@/helpers/statesmen"

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
      const masterOfHorse =
        combatCalculation.masterOfHorse === commander
          ? null
          : combatCalculation.masterOfHorse
      updateCombatCalculation({ ...combatCalculation, commander, masterOfHorse })
    }
  }

  const war = publicGameState.wars.find(
    (war: War) => war.id === combatCalculation.war,
  )

  const enemyLeaders = publicGameState.enemyLeaders.filter(
    (leader: EnemyLeader) => leader.seriesName === war?.seriesName,
  )

  const setWar = (warId: number | null) => {
    if (combatCalculation.war !== warId) {
      const newWar =
        warId !== null
          ? publicGameState.wars.find((w: War) => w.id === warId)
          : undefined
      const newBattle: "land" | "naval" = newWar
        ? newWar.navalStrength > 0
          ? "naval"
          : "land"
        : combatCalculation.battle
      updateCombatCalculation({
        ...combatCalculation,
        war: warId,
        battle: newBattle,
      })
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

  const setIsDictator = (value: boolean) => {
    updateCombatCalculation({
      ...combatCalculation,
      isDictator: value,
      masterOfHorse: value ? combatCalculation.masterOfHorse : null,
    })
  }

  const setMasterOfHorse = (value: number | null) => {
    updateCombatCalculation({ ...combatCalculation, masterOfHorse: value })
  }

  const mohSenator =
    combatCalculation.isDictator && combatCalculation.masterOfHorse
      ? (publicGameState.senators.find(
          (s: Senator) => s.id === combatCalculation.masterOfHorse,
        ) ?? null)
      : null

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
  const combinedMilitary =
    (commander?.military ?? 0) + (mohSenator?.military ?? 0)
  forceStrength += Math.min(combinedMilitary, forceStrength)
  const matchingWarMultiplier = war?.seriesName
    ? Math.max(
        1,
        publicGameState.wars.filter(
          (w) => w.seriesName === war.seriesName && w.status === "active",
        ).length,
      )
    : 1
  const baseWarStrength =
    (combatCalculation.battle === "land"
      ? war?.landStrength
      : war?.navalStrength) ?? 0
  const leaderStrength = enemyLeaders.reduce((sum, l) => sum + l.strength, 0)
  const warStrength = baseWarStrength * matchingWarMultiplier + leaderStrength
  const modifier = forceStrength - warStrength

  const disastersNullified =
    !!commander?.statesmanName &&
    !!war?.seriesName &&
    SERIES_NULLIFIERS[commander.code] === war.seriesName

  const effectiveDisasterNumbers = [
    ...(disastersNullified ? [] : (war?.disasterNumbers ?? [])),
    ...enemyLeaders.map((l) => l.disasterNumber),
  ]
  const effectiveStandoffNumbers = [
    ...(disastersNullified ? [] : (war?.standoffNumbers ?? [])),
    ...enemyLeaders.map((l) => l.standoffNumber),
  ]

  const ignoredNumbers = [
    ...effectiveStandoffNumbers,
    ...effectiveDisasterNumbers,
  ]
  const victoryProbability = Math.round(
    getDiceProbability(3, modifier, { min: 14 }, ignoredNumbers) * 100,
  )
  const stalemateProbability = Math.round(
    getDiceProbability(3, modifier, { min: 8, max: 13 }, ignoredNumbers) * 100,
  )
  const defeatProbability = Math.round(
    getDiceProbability(3, modifier, { max: 7 }, ignoredNumbers) * 100,
  )
  const standoffProbability = Math.round(
    getDiceProbability(3, 0, { exacts: effectiveStandoffNumbers }) * 100,
  )
  const disasterProbability = Math.round(
    getDiceProbability(3, 0, { exacts: effectiveDisasterNumbers }) * 100,
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
              className="relative h-6 min-w-6 rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
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
              className="relative h-6 min-w-6 rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
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
        <div className="flex flex-col gap-2">
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
              {[...publicGameState.senators]
                .sort((a, b) => a.familyName.localeCompare(b.familyName))
                .map((senator: Senator) => (
                  <option key={senator.id} value={senator.id}>
                    {senator.displayName} ({senator.military})
                  </option>
                ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is-dictator"
              checked={combatCalculation.isDictator}
              onChange={(e) => setIsDictator(e.target.checked)}
              disabled={isReadOnly}
              className="rounded border-blue-600 disabled:cursor-not-allowed"
            />
            <label htmlFor="is-dictator" className="font-semibold">
              Dictator
            </label>
          </div>
          {combatCalculation.isDictator && (
            <div className="flex flex-col gap-1">
              <label htmlFor="master-of-horse" className="font-semibold">
                Master of Horse{" "}
                <span className="text-sm font-normal text-neutral-600">
                  (military skill)
                </span>
              </label>
              <select
                id="master-of-horse"
                value={combatCalculation.masterOfHorse ?? ""}
                onChange={(e) =>
                  setMasterOfHorse(
                    e.target.value !== "" ? Number(e.target.value) : null,
                  )
                }
                disabled={isReadOnly}
                className="rounded-md border border-blue-600 p-1 disabled:cursor-not-allowed disabled:bg-neutral-100"
              >
                <option value="">-- select an option --</option>
                {[...publicGameState.senators]
                  .filter((s: Senator) => s.id !== combatCalculation.commander)
                  .sort((a, b) => a.familyName.localeCompare(b.familyName))
                  .map((senator: Senator) => (
                    <option key={senator.id} value={senator.id}>
                      {senator.displayName} ({senator.military})
                    </option>
                  ))}
              </select>
            </div>
          )}
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
                  ? "border-blue-600 bg-blue-100 text-blue-800"
                  : "border-neutral-400 text-neutral-600 hover:bg-neutral-100 disabled:hover:bg-transparent"
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
                ? "border-green-600 bg-green-100 text-green-800"
                : "border-neutral-400 text-neutral-600 hover:bg-neutral-100 disabled:hover:bg-transparent"
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
                    <strong className="font-semibold">Risky command</strong>:
                    commander consent is required for such a dangerous
                    deployment
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
