"use client"

import Senator from "@/classes/Senator"
import useCustomActionForm from "@/hooks/useCustomActionForm"

import ActionDescription from "../ActionDescription"
import { CustomActionFormProps } from "../ActionDispatcher"

interface AssassinationRow {
  result: string
  description: string
  chance: (modifier: number) => string
}

const percentage = (lo: number, hi: number): string => {
  const clamped_lo = Math.max(1, lo)
  const clamped_hi = Math.min(6, hi)
  if (clamped_lo > clamped_hi) return "0%"
  const count = clamped_hi - clamped_lo + 1
  return `${Math.round((count / 6) * 100)}%`
}

const ASSASSINATION_TABLE: AssassinationRow[] = [
  {
    result: "Caught",
    description: "Assassin is executed",
    chance: (mod) => percentage(1, 2 - mod),
  },
  {
    result: "No Effect",
    description: "Target survives",
    chance: (mod) => percentage(3 - mod, 4 - mod),
  },
  {
    result: "Killed",
    description: "Target is assassinated",
    chance: (mod) => percentage(5 - mod, 6),
  },
]

const AttemptAssassinationForm = ({
  availableAction,
  publicGameState,
  privateGameState,
  selection,
  setSelection,
  isExpanded,
  setIsExpanded,
  onSubmitSuccess,
}: CustomActionFormProps) => {
  const {
    dialogRef,
    feedback,
    loading,
    openDialog,
    closeDialog,
    handleDialogClose,
    submit,
  } = useCustomActionForm({
    availableAction,
    publicGameState,
    isExpanded,
    setIsExpanded,
    onSubmitSuccess,
  })

  const myFactionId = availableAction.faction

  const ownSenators = publicGameState.senators
    .filter(
      (s: Senator) =>
        s.alive && s.location === "Rome" && s.faction === myFactionId,
    )
    .sort((a: Senator, b: Senator) => a.familyName.localeCompare(b.familyName))

  // Build targetable senators grouped by faction, excluding already-targeted factions
  const targetableFactions = publicGameState.factions.filter(
    (f) =>
      f.id !== myFactionId && !f.statusItems.includes("assassination targeted"),
  )

  const targetableSenators = publicGameState.senators
    .filter(
      (s: Senator) =>
        s.alive &&
        s.location === "Rome" &&
        s.faction !== null &&
        s.faction !== myFactionId &&
        targetableFactions.some((f) => f.id === s.faction),
    )
    .sort((a: Senator, b: Senator) => a.familyName.localeCompare(b.familyName))

  const assassinCardCount =
    privateGameState.faction?.cards.filter((c) => c === "assassin").length ?? 0

  const assassinId = (selection["Assassin"] as string) ?? ""
  const targetId = (selection["Target"] as string) ?? ""
  const assassinCards = parseInt((selection["Assassin cards"] as string) ?? "0")

  const setAssassinCards = (val: number) => {
    const clamped = Math.max(0, Math.min(assassinCardCount, val))
    setSelection((prev) => ({
      ...(prev ?? {}),
      "Assassin cards": String(clamped),
    }))
  }

  const modifier = assassinCards

  const targetSenator = targetId
    ? publicGameState.senators.find((s: Senator) => String(s.id) === targetId)
    : null
  const targetFactionCardCount = targetSenator
    ? (publicGameState.factions.find((f) => f.id === targetSenator.faction)
        ?.cardCount ?? 0)
    : 0

  const canSubmit = !!assassinId && !!targetId

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!canSubmit) return
    const payload: Record<string, unknown> = {
      Assassin: assassinId,
      Target: targetId,
    }
    if (assassinCardCount > 0) {
      payload["Assassin cards"] = String(assassinCards)
    }
    await submit(payload)
  }

  return (
    <form onSubmit={handleSubmit}>
      <button
        type="button"
        onClick={openDialog}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        {availableAction.name}...
      </button>

      <dialog
        ref={dialogRef}
        onClose={handleDialogClose}
        className="min-w-[24rem] rounded-lg bg-white p-6 shadow-lg"
      >
        <div className="flex flex-col gap-6">
          <div className="flex w-0 min-w-full flex-col gap-4">
            <h3 className="text-xl">{availableAction.name}</h3>
            <ActionDescription
              actionName={availableAction.name}
              context={availableAction.context}
            />
          </div>

          {feedback && (
            <div className="inline-flex rounded-md bg-red-50 px-2 py-1 text-red-600">
              <p>{feedback}</p>
            </div>
          )}

          <div className="flex w-0 min-w-full flex-col gap-6">
            {/* Assassin selector */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold">Assassin</label>
              <select
                value={assassinId}
                onChange={(e) =>
                  setSelection((prev) => ({
                    ...(prev ?? {}),
                    Assassin: e.target.value,
                  }))
                }
                required
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select a senator --</option>
                {ownSenators.map((s) => (
                  <option key={s.id} value={String(s.id)}>
                    {s.displayName}
                  </option>
                ))}
              </select>
            </div>

            {/* Target selector, grouped by faction */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold">Target</label>
              <select
                value={targetId}
                onChange={(e) =>
                  setSelection((prev) => ({
                    ...(prev ?? {}),
                    Target: e.target.value,
                  }))
                }
                required
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select a senator --</option>
                {targetableFactions.map((faction) => {
                  const senators = targetableSenators.filter(
                    (s) => s.faction === faction.id,
                  )
                  if (senators.length === 0) return null
                  return (
                    <optgroup key={faction.id} label={faction.displayName}>
                      {senators.map((s) => (
                        <option key={s.id} value={String(s.id)}>
                          {s.displayName}
                        </option>
                      ))}
                    </optgroup>
                  )
                })}
              </select>
            </div>

            {/* Assassin cards input */}
            {assassinCardCount > 0 && (
              <div className="flex flex-col gap-1">
                <label className="font-semibold">Assassin cards to play</label>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setAssassinCards(assassinCards - 1)}
                      disabled={assassinCards <= 0}
                      className="relative h-6 min-w-6 rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                    >
                      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                        &minus;
                      </div>
                    </button>
                    <input
                      type="number"
                      min={0}
                      max={assassinCardCount}
                      value={assassinCards}
                      onChange={(e) =>
                        setAssassinCards(parseInt(e.target.value) || 0)
                      }
                      className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5"
                    />
                    <button
                      type="button"
                      onClick={() => setAssassinCards(assassinCards + 1)}
                      disabled={assassinCards >= assassinCardCount}
                      className="relative h-6 min-w-6 rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                    >
                      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                        +
                      </div>
                    </button>
                  </div>
                  {assassinCardCount > 0 && (
                    <div className="flex w-full items-center justify-center">
                      <button
                        type="button"
                        className={`w-10 cursor-default px-2 text-sm ${assassinCards !== 0 && "text-neutral-400"}`}
                        onClick={() => setAssassinCards(0)}
                      >
                        0
                      </button>
                      <input
                        type="range"
                        min={0}
                        max={assassinCardCount}
                        value={assassinCards}
                        onChange={(e) =>
                          setAssassinCards(Number(e.target.value))
                        }
                        className="w-full"
                      />
                      <button
                        type="button"
                        className={`w-10 cursor-default px-2 text-sm ${assassinCards !== assassinCardCount && "text-neutral-400"}`}
                        onClick={() => setAssassinCards(assassinCardCount)}
                      >
                        {assassinCardCount}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Assassination table */}
            <div className="flex flex-col gap-1">
              <p className="font-semibold">
                Assassination table
                {modifier > 0 && (
                  <span className="ml-1 font-normal text-neutral-500">
                    (+{modifier} modifier)
                  </span>
                )}
              </p>
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="border-b border-neutral-200">
                    <th className="py-1 pr-4 text-left font-semibold">
                      Chance
                    </th>
                    <th className="py-1 pr-4 text-left font-semibold">
                      Result
                    </th>
                    <th className="py-1 text-left font-semibold">Effect</th>
                  </tr>
                </thead>
                <tbody>
                  {ASSASSINATION_TABLE.map((row) => (
                    <tr
                      key={row.result}
                      className="border-b border-neutral-100"
                    >
                      <td className="py-1 pr-4">{row.chance(modifier)}</td>
                      <td className="py-1 pr-4">{row.result}</td>
                      <td className="py-1 text-neutral-600">
                        {row.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {targetFactionCardCount > 0 && (
                <p className="mt-2 text-sm text-neutral-500">
                  The target&apos;s faction may hold a secret bodyguard that
                  could change the outcome.
                </p>
              )}
            </div>
          </div>

          <div className="mt-4 flex justify-end gap-4">
            <button
              type="button"
              onClick={closeDialog}
              className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !canSubmit}
              className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
            >
              Confirm
            </button>
          </div>
        </div>
      </dialog>
    </form>
  )
}

export default AttemptAssassinationForm
