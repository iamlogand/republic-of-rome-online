"use client"

import { AllocationEntry } from "@/classes/AvailableAction"
import Senator from "@/classes/Senator"
import { pluralize } from "@/helpers/text"
import useCustomActionForm from "@/hooks/useCustomActionForm"

import { CustomActionFormProps } from "../ActionBar"
import NumberInput from "../NumberInput"

const RedistributeTalentsForm = ({
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

  const factionId = availableAction.faction
  const treasury = privateGameState.faction?.treasury ?? 0

  const ownSenators: Senator[] = publicGameState.senators
    .filter((s) => s.faction === factionId && s.alive)
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const total = ownSenators.reduce((sum, s) => sum + s.talents, 0) + treasury

  const entries: AllocationEntry[] = [
    ...ownSenators.map((s) => ({
      id: `senator:${s.id}`,
      name: s.displayName,
      default: s.talents,
    })),
    { id: "faction_treasury", name: "Faction treasury", default: treasury },
  ]

  const alloc = (selection["Allocation"] ?? {}) as { [id: string]: number }

  const getEntryValue = (entry: AllocationEntry) =>
    alloc[entry.id] ?? entry.default

  const allocTotal = entries.reduce((sum, e) => sum + getEntryValue(e), 0)
  const balanced = allocTotal === total

  const updateEntry = (id: string, newValue: number) => {
    setSelection((prev) => ({
      ...(prev ?? {}),
      Allocation: {
        ...((prev?.["Allocation"] ?? {}) as { [id: string]: number }),
        [id]: newValue,
      },
    }))
  }

  const handleClear = () => {
    const newAlloc: { [id: string]: number } = {}
    entries.forEach((entry) => {
      newAlloc[entry.id] = 0
    })
    setSelection((prev) => ({ ...(prev ?? {}), Allocation: newAlloc }))
  }

  const handleReset = () => {
    const newAlloc: { [id: string]: number } = {}
    entries.forEach((entry) => {
      newAlloc[entry.id] = entry.default
    })
    setSelection((prev) => ({ ...(prev ?? {}), Allocation: newAlloc }))
  }

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    const allocation = Object.fromEntries(
      entries.map((e) => [e.id, getEntryValue(e)]),
    )
    await submit({ Allocation: allocation })
  }

  return (
    <form onSubmit={handleSubmit}>
      <button
        type="button"
        onClick={openDialog}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        Redistribute talents...
      </button>

      <dialog
        ref={dialogRef}
        onClose={handleDialogClose}
        className="min-w-[24rem] rounded-lg bg-white p-6 shadow-lg"
      >
        <div className="flex flex-col gap-6">
          <div className="flex w-0 min-w-full flex-col gap-4">
            <h3 className="text-xl">Redistribute talents</h3>
            <p>Move talents between your senators and faction treasury.</p>
            <p className="text-sm">
              Senators spend their personal treasuries on votes and bribes. The
              faction treasury keeps your talents safe and defends against
              persuasion attempts.
            </p>
          </div>
          {feedback && (
            <div className="inline-flex rounded-md bg-red-50 px-2 py-1 text-red-600">
              <p>{feedback}</p>
            </div>
          )}
          <div className="flex items-baseline justify-between gap-3">
            <span
              className={`min-w-[180px] ${balanced ? "text-neutral-600" : "text-red-600"}`}
            >
              Total: {allocTotal} / {pluralize(total, "talent")}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleClear}
                className="select-none rounded-md border border-neutral-600 px-3 py-1 text-sm text-neutral-600 hover:text-neutral-600"
              >
                Clear
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="select-none rounded-md border border-neutral-600 px-3 py-1 text-sm text-neutral-600 hover:text-neutral-600"
              >
                Reset
              </button>
            </div>
          </div>
          <div className="flex flex-col gap-1">
            {entries.map((entry) => {
              const value = getEntryValue(entry)
              const remaining = total - allocTotal
              const maxValue = value + remaining
              return (
                <NumberInput
                  key={entry.id}
                  label={entry.name}
                  value={value}
                  onChange={(v) =>
                    updateEntry(entry.id, Math.max(0, Math.min(maxValue, v)))
                  }
                  min={0}
                  max={maxValue}
                  hideSlider
                />
              )
            })}
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
              className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
              disabled={loading || !balanced}
            >
              Confirm
            </button>
          </div>
        </div>
      </dialog>
    </form>
  )
}

export default RedistributeTalentsForm
