"use client"

import PublicGameState from "@/classes/PublicGameState"
import { getEvilOmensLevel } from "@/helpers/gameEffects"
import { calculatePersuasion } from "@/helpers/persuasion"

import Checkbox from "./Checkbox"
import NumberInput from "./NumberInput"

export interface PersuasionCalculationState {
  id: number
  persuaderId: number | null
  targetId: number | null
  persuaderBribe: number
  counterBribes: number
  evilOmens: number
  eraEnds: boolean
}

interface Props {
  calculation: PersuasionCalculationState
  publicGameState: PublicGameState
  updateCalculation: (
    update: Partial<Omit<PersuasionCalculationState, "id">>,
  ) => void
}

const PersuasionCalculationPanel = ({
  calculation,
  publicGameState,
  updateCalculation,
}: Props) => {
  const eligibleSenators = publicGameState.senators.filter(
    (s) => s.alive && s.location === "Rome",
  )

  const persuader =
    eligibleSenators.find((s) => s.id === calculation.persuaderId) ?? null
  const target =
    eligibleSenators.find((s) => s.id === calculation.targetId) ?? null

  const actualEvilOmens = getEvilOmensLevel(publicGameState.game?.effects ?? [])

  const availableTargets = eligibleSenators.filter(
    (s) =>
      s.id !== calculation.persuaderId &&
      !(
        persuader !== null &&
        persuader.faction !== null &&
        s.faction === persuader.faction
      ),
  )

  const result =
    persuader && target
      ? calculatePersuasion({
          oratory: persuader.oratory,
          influence: persuader.influence,
          loyalty: target.loyalty,
          targetTalents: target.talents,
          alignedTarget: target.faction !== null,
          persuaderBribe: calculation.persuaderBribe,
          counterBribes: calculation.counterBribes,
          evilOmens: calculation.evilOmens,
          eraEnds: calculation.eraEnds,
        })
      : null

  const persuaderGroupList = publicGameState.factions
    .filter((faction) => eligibleSenators.some((s) => s.faction === faction.id))
    .map((faction) => ({
      id: faction.id,
      label: faction.displayName,
      senators: eligibleSenators
        .filter((s) => s.faction === faction.id)
        .sort((a, b) => (b.oratory + b.influence) - (a.oratory + a.influence)),
    }))
  if (eligibleSenators.some((s) => s.faction === null)) {
    persuaderGroupList.push({
      id: -1,
      label: "Unaligned",
      senators: eligibleSenators
        .filter((s) => s.faction === null)
        .sort((a, b) => (b.oratory + b.influence) - (a.oratory + a.influence)),
    })
  }

  const targetGroupList = publicGameState.factions
    .filter((faction) => availableTargets.some((s) => s.faction === faction.id))
    .map((faction) => ({
      id: faction.id,
      label: faction.displayName,
      senators: availableTargets
        .filter((s) => s.faction === faction.id)
        .sort((a, b) => (a.loyalty + a.talents) - (b.loyalty + b.talents)),
    }))
  if (availableTargets.some((s) => s.faction === null)) {
    targetGroupList.push({
      id: -1,
      label: "Unaligned",
      senators: availableTargets
        .filter((s) => s.faction === null)
        .sort((a, b) => (a.loyalty + a.talents) - (b.loyalty + b.talents)),
    })
  }

  const clampValue = (value: number, maximum?: number) =>
    Math.max(
      0,
      Math.min(maximum ?? Number.MAX_SAFE_INTEGER, Math.floor(value || 0)),
    )

  return (
    <>
      <div className="grid grid-cols-2 gap-12">
        <div className="flex flex-col gap-6">
          <div className="flex flex-col gap-1">
            <label
              htmlFor={`persuader-${calculation.id}`}
              className="font-semibold"
            >
              Persuader
            </label>
            <select
              id={`persuader-${calculation.id}`}
              value={calculation.persuaderId ?? ""}
              onChange={(event) => {
                const newPersuaderId = event.target.value
                  ? Number(event.target.value)
                  : null
                const newPersuader =
                  eligibleSenators.find((s) => s.id === newPersuaderId) ?? null
                const targetBecomesInvalid =
                  newPersuader !== null &&
                  newPersuader.faction !== null &&
                  target?.faction === newPersuader.faction
                updateCalculation({
                  persuaderId: newPersuaderId,
                  ...(targetBecomesInvalid ? { targetId: null } : {}),
                })
              }}
              className="rounded-md border border-blue-600 p-1"
            >
              <option value="">-- select an option --</option>
              {persuaderGroupList.map((group) => (
                <optgroup key={group.id} label={group.label}>
                  {group.senators.map((senator) => (
                    <option key={senator.id} value={senator.id}>
                      {senator.displayName} (ORA {senator.oratory}, INF{" "}
                      {senator.influence}, {senator.talents}T)
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <NumberInput
              id={`persuader-bribe-${calculation.id}`}
              label="Persuader bribe"
              value={calculation.persuaderBribe}
              min={0}
              onChange={(value) =>
                updateCalculation({ persuaderBribe: clampValue(value) })
              }
            />
            {persuader && (
              <p className="text-sm text-neutral-500">
                Selected persuader has{" "}
                <button
                  type="button"
                  className="text-blue-600 hover:underline"
                  onClick={() =>
                    updateCalculation({ persuaderBribe: persuader.talents })
                  }
                >
                  {persuader.talents}T
                </button>
              </p>
            )}
          </div>

          <Checkbox
            checked={calculation.eraEnds}
            onChange={(checked) => updateCalculation({ eraEnds: checked })}
          >
            Era Ends
          </Checkbox>

          {actualEvilOmens > 0 && (
            <NumberInput
              id={`evil-omens-${calculation.id}`}
              label="Evil omens"
              value={calculation.evilOmens}
              min={0}
              max={actualEvilOmens}
              onChange={(value) =>
                updateCalculation({
                  evilOmens: clampValue(value, actualEvilOmens),
                })
              }
            />
          )}
        </div>

        <div className="flex flex-col gap-6">
          <div className="flex flex-col gap-1">
            <label
              htmlFor={`target-${calculation.id}`}
              className="font-semibold"
            >
              Target
            </label>
            <select
              id={`target-${calculation.id}`}
              value={calculation.targetId ?? ""}
              onChange={(event) =>
                updateCalculation({
                  targetId: event.target.value
                    ? Number(event.target.value)
                    : null,
                })
              }
              className="rounded-md border border-blue-600 p-1"
            >
              <option value="">-- select an option --</option>
              {targetGroupList.map((group) => (
                <optgroup key={group.id} label={group.label}>
                  {group.senators.map((senator) => (
                    <option key={senator.id} value={senator.id}>
                      {senator.displayName} (LOY {senator.loyalty},{" "}
                      {senator.talents}T)
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <NumberInput
              id={`counter-bribe-${calculation.id}`}
              label="Talents and counter-bribes"
              value={calculation.counterBribes}
              min={0}
              onChange={(value) =>
                updateCalculation({ counterBribes: clampValue(value) })
              }
            />
            {target && (
              <p className="text-sm text-neutral-500">
                Selected target has{" "}
                <button
                  type="button"
                  className="text-blue-600 hover:underline"
                  onClick={() =>
                    updateCalculation({ counterBribes: target.talents })
                  }
                >
                  {target.talents}T
                </button>
              </p>
            )}
          </div>
        </div>
      </div>

      <div
        aria-live="polite"
        className="mt-6 rounded-md bg-blue-50 px-4 py-4 text-center text-blue-700"
      >
        <div className="text-sm">Chance of success</div>
        <strong className="text-3xl">
          {result ? `${result.chancePercent}%` : "—"}
        </strong>
      </div>
    </>
  )
}

export default PersuasionCalculationPanel
