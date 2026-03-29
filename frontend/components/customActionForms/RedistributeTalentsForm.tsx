"use client"

import { useEffect, useRef, useState } from "react"

import { AllocationEntry } from "@/classes/AvailableAction"
import Senator from "@/classes/Senator"
import getCSRFToken from "@/helpers/csrf"

import ActionDescription from "../ActionDescription"
import { CustomActionFormProps } from "../ActionDispatcher"

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
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [feedback, setFeedback] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)

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

  const initializeAllocation = () => {
    setSelection((prev) => {
      const existingAlloc = (prev?.["Allocation"] ?? {}) as {
        [id: string]: number
      }
      const newAlloc: { [id: string]: number } = {}
      entries.forEach((entry) => {
        newAlloc[entry.id] = existingAlloc[entry.id] ?? entry.default
      })
      return { ...(prev ?? {}), Allocation: newAlloc }
    })
  }

  const openDialog = () => {
    initializeAllocation()
    dialogRef.current?.showModal()
    setIsExpanded?.(true)
  }

  const handleDialogClose = () => {
    setFeedback("")
    setIsExpanded?.(false)
  }

  const closeDialog = () => {
    dialogRef.current?.close()
  }

  useEffect(() => {
    if (isExpanded) {
      initializeAllocation()
      dialogRef.current?.showModal()
    }
  }, [isExpanded])

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!publicGameState.game) return
    setLoading(true)
    const csrfToken = getCSRFToken()

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_ORIGIN}/api/games/${publicGameState.game.id}/submit-action/${availableAction.id}`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(selection),
      },
    )
    setLoading(false)
    if (response.ok) {
      closeDialog()
      onSubmitSuccess?.()
    } else {
      const result = await response.json()
      if (result.message) {
        setFeedback(result.message)
      }
    }
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
        className="rounded-lg bg-white p-6 shadow-lg"
      >
        <div className="flex flex-col gap-6">
          <div className="flex max-w-[400px] flex-col gap-4">
            <h3 className="text-xl">{availableAction.name}</h3>
            <ActionDescription
              actionName={availableAction.name}
              context={availableAction.context}
            />
          </div>
          {feedback && (
            <div className="inline-flex max-w-[400px] rounded-md bg-red-50 px-2 py-1 text-red-600">
              <p>{feedback}</p>
            </div>
          )}
          <div className="flex items-baseline justify-between gap-3">
            <span
              className={`${balanced ? "text-neutral-600" : "text-red-600"}`}
            >
              Total: {allocTotal} / {total} {total === 1 ? "talent" : "talents"}
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
                <div
                  key={entry.id}
                  className="flex items-center justify-between gap-2"
                >
                  <label htmlFor={`allocation-${entry.id}`}>{entry.name}</label>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => updateEntry(entry.id, value - 1)}
                      disabled={value <= 0}
                      className="relative h-6 min-w-6 rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                    >
                      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                        &minus;
                      </div>
                    </button>
                    <input
                      id={`allocation-${entry.id}`}
                      type="number"
                      min={0}
                      max={maxValue}
                      value={value}
                      onChange={(e) => {
                        const newVal = Math.max(
                          0,
                          Math.min(maxValue, Number(e.target.value)),
                        )
                        updateEntry(entry.id, newVal)
                      }}
                      className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5"
                    />
                    <button
                      type="button"
                      onClick={() => updateEntry(entry.id, value + 1)}
                      disabled={remaining <= 0}
                      className="relative h-6 min-w-6 rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                    >
                      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                        +
                      </div>
                    </button>
                  </div>
                </div>
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
              className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:opacity-50"
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
