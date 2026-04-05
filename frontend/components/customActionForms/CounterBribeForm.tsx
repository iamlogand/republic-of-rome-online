"use client"

import { useEffect, useRef, useState } from "react"

import getCSRFToken from "@/helpers/csrf"

import { CustomActionFormProps } from "../ActionDispatcher"
import PersuasionPanel from "./sharedPanels/PersuasionPanel"

const CounterBribeForm = ({
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

  const threshold = 10
  const maxTalents = privateGameState.faction?.treasury ?? 0

  const newCounterBribe = parseInt((selection["Talents"] as string) ?? "0")

  const setTalents = (value: number) => {
    const clamped = Math.max(0, Math.min(maxTalents, value))
    setSelection((prev) => ({ ...(prev ?? {}), Talents: String(clamped) }))
  }

  const persuader = publicGameState.senators.find((s) =>
    s.statusItems.includes("persuader"),
  )
  const target = publicGameState.senators.find((s) =>
    s.statusItems.includes("persuasion target"),
  )
  const bribe = (() => {
    const item = persuader?.statusItems.find((s) => s.startsWith("bribed "))
    return item ? parseInt(item.split(" ")[1]) : 0
  })()
  const modifier =
    persuader && target
      ? persuader.oratory +
        persuader.influence +
        2 * bribe -
        target.loyalty -
        target.talents -
        (target.faction ? 7 : 0) -
        newCounterBribe
      : 0

  const initializeTalents = () => {
    setSelection((prev) => ({
      ...(prev ?? {}),
      Talents: (prev ?? {})["Talents"] ?? "0",
    }))
  }

  const openDialog = () => {
    initializeTalents()
    dialogRef.current?.showModal()
    setIsExpanded?.(true)
  }

  const handleDialogClose = () => {
    setFeedback("")
    setIsExpanded?.(false)
  }

  const closeDialog = () => {
    dialogRef.current?.close()
    setIsExpanded?.(false)
  }

  useEffect(() => {
    if (isExpanded) {
      initializeTalents()
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
      setSelection({})
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
        Counter-bribe...
      </button>

      <dialog
        ref={dialogRef}
        onClose={handleDialogClose}
        className="min-w-80 rounded-lg bg-white p-6 shadow-lg"
      >
        <div className="flex flex-col gap-6">
          <div className="flex w-0 min-w-full flex-col gap-4">
            <h3 className="text-xl">Counter-bribe</h3>
            <p>
              Prevent persuasion by transferring talents from your faction
              treasury to {persuader?.displayName} as a counter-bribe.
            </p>
          </div>
          {feedback && (
            <div className="inline-flex rounded-md bg-red-50 px-2 py-1 text-red-600">
              <p>{feedback}</p>
            </div>
          )}
          <PersuasionPanel
            bribe={newCounterBribe}
            setBribe={setTalents}
            maxBribe={maxTalents}
            modifier={modifier}
            threshold={threshold}
            label="Talents"
          />
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
              disabled={loading || newCounterBribe < 1}
              className="select-none rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:opacity-50"
            >
              Confirm
            </button>
          </div>
        </div>
      </dialog>
    </form>
  )
}

export default CounterBribeForm
