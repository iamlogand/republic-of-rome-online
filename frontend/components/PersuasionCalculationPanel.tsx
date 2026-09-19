"use client"

import { useMemo } from "react"

import { PersuasionSnapshot, calculatePersuasion } from "@/helpers/persuasion"

import Checkbox from "./Checkbox"

export interface PersuasionCalculationState {
  id: number
  persuaderId: number | null
  targetId: number | null
  persuaderBribe: number
  counterBribes: Record<number, number>
  useSeduction: boolean
  useBlackmail: boolean
}

interface Props {
  calculation: PersuasionCalculationState
  snapshot: PersuasionSnapshot
  updateCalculation: (
    update: Partial<Omit<PersuasionCalculationState, "id">>,
  ) => void
}

const PersuasionCalculationPanel = ({
  calculation,
  snapshot,
  updateCalculation,
}: Props) => {
  const persuader = snapshot.persuaders.find(
    (senator) => senator.id === calculation.persuaderId,
  )
  const target = snapshot.targets.find(
    (senator) => senator.id === calculation.targetId,
  )
  const unopposed = calculation.useSeduction || calculation.useBlackmail
  const counterBribeTotal = Object.values(calculation.counterBribes).reduce(
    (total, value) => total + value,
    0,
  )
  const effectiveCounterBribes = unopposed ? 0 : counterBribeTotal
  const result =
    persuader && target
      ? calculatePersuasion({
          oratory: persuader.oratory,
          influence: persuader.influence,
          loyalty: target.loyalty,
          targetTalents: target.talents,
          alignedTarget: target.faction !== null,
          persuaderBribe: calculation.persuaderBribe,
          counterBribes: effectiveCounterBribes,
          evilOmens: snapshot.evilOmens,
          eraEnds: snapshot.eraEnds,
        })
      : null

  const targetGroups = useMemo(() => {
    const groups = snapshot.factions
      .filter((faction) =>
        snapshot.targets.some((senator) => senator.faction === faction.id),
      )
      .map((faction) => ({
        id: faction.id,
        label: faction.displayName,
        senators: snapshot.targets.filter(
          (senator) => senator.faction === faction.id,
        ),
      }))

    if (snapshot.targets.some((senator) => senator.faction === null)) {
      groups.push({
        id: -1,
        label: "Unaligned",
        senators: snapshot.targets.filter(
          (senator) => senator.faction === null,
        ),
      })
    }
    return groups
  }, [snapshot])

  const clampValue = (value: number, maximum?: number) =>
    Math.max(
      0,
      Math.min(maximum ?? Number.MAX_SAFE_INTEGER, Math.floor(value || 0)),
    )

  const setCounterBribe = (factionId: number, value: number) =>
    updateCalculation({
      counterBribes: {
        ...calculation.counterBribes,
        [factionId]: clampValue(value),
      },
    })

  return (
    <div className="grid grid-cols-2 gap-8">
      <div className="flex flex-col gap-4">
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
            onChange={(event) =>
              updateCalculation({
                persuaderId: event.target.value
                  ? Number(event.target.value)
                  : null,
                persuaderBribe: 0,
              })
            }
            className="rounded-md border border-blue-600 p-1"
          >
            <option value="">-- select an option --</option>
            {snapshot.persuaders.map((senator) => (
              <option key={senator.id} value={senator.id}>
                {senator.displayName} (ORA {senator.oratory}, INF{" "}
                {senator.influence}, {senator.talents}T)
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor={`target-${calculation.id}`} className="font-semibold">
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
            {targetGroups.map((group) => (
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
          <label
            htmlFor={`persuader-bribe-${calculation.id}`}
            className="font-semibold"
          >
            Persuader bribe
          </label>
          <input
            id={`persuader-bribe-${calculation.id}`}
            type="number"
            min={0}
            max={persuader?.talents ?? 0}
            value={calculation.persuaderBribe}
            onChange={(event) =>
              updateCalculation({
                persuaderBribe: clampValue(
                  Number(event.target.value),
                  persuader?.talents ?? 0,
                ),
              })
            }
            disabled={!persuader}
            className="rounded-md border border-blue-600 px-2 py-1 disabled:border-neutral-300 disabled:bg-neutral-100"
          />
        </div>

        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 font-semibold">Cards</legend>
          <Checkbox
            checked={calculation.useSeduction}
            onChange={(checked) =>
              updateCalculation({
                useSeduction: checked,
                useBlackmail: checked ? false : calculation.useBlackmail,
              })
            }
          >
            Seduction
          </Checkbox>
          <Checkbox
            checked={calculation.useBlackmail}
            onChange={(checked) =>
              updateCalculation({
                useBlackmail: checked,
                useSeduction: checked ? false : calculation.useSeduction,
              })
            }
          >
            Blackmail
          </Checkbox>
          <p className="text-sm text-neutral-600">
            Card availability is not checked. Either card makes the attempt
            unopposed.
          </p>
        </fieldset>
      </div>

      <div className="flex flex-col gap-5">
        <fieldset className="flex flex-col gap-3">
          <legend className="mb-1 font-semibold">Counter-bribes</legend>
          {snapshot.factions.map((faction) => (
            <div
              key={faction.id}
              className="grid grid-cols-[1fr_6rem] items-center gap-3"
            >
              <label htmlFor={`counter-bribe-${calculation.id}-${faction.id}`}>
                {faction.displayName}
              </label>
              <input
                id={`counter-bribe-${calculation.id}-${faction.id}`}
                type="number"
                min={0}
                value={calculation.counterBribes[faction.id] ?? 0}
                onChange={(event) =>
                  setCounterBribe(faction.id, Number(event.target.value))
                }
                disabled={unopposed}
                className="rounded-md border border-blue-600 px-2 py-1 disabled:border-neutral-300 disabled:bg-neutral-100"
              />
            </div>
          ))}
          <div className="grid grid-cols-[1fr_6rem] gap-3 border-t border-neutral-300 pt-2 font-semibold">
            <span>Total</span>
            <span className="px-2">
              {unopposed ? "Ignored" : `${counterBribeTotal}T`}
            </span>
          </div>
        </fieldset>

        <dl className="grid grid-cols-[1fr_auto] gap-x-4 gap-y-2 rounded-md bg-neutral-100 px-3 py-2 text-sm">
          <dt>Evil Omens</dt>
          <dd>{snapshot.evilOmens}</dd>
          <dt>Era Ends</dt>
          <dd>{snapshot.eraEnds ? "Yes" : "No"}</dd>
        </dl>

        <div
          aria-live="polite"
          className="rounded-md bg-blue-50 px-4 py-4 text-center text-blue-700"
        >
          <div className="text-sm">Chance of success</div>
          <strong className="text-3xl">
            {result ? `${result.chancePercent}%` : "—"}
          </strong>
        </div>
      </div>
    </div>
  )
}

export default PersuasionCalculationPanel
