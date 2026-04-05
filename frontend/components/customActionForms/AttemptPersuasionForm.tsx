"use client"

import { useEffect, useRef, useState } from "react"

import getCSRFToken from "@/helpers/csrf"

import { CustomActionFormProps } from "../ActionDispatcher"
import PersuasionPanel from "./sharedPanels/PersuasionPanel"

const FACTION_LEADER = "faction leader"

const AttemptPersuasionForm = ({
  availableAction,
  publicGameState,
  isExpanded,
  setIsExpanded,
  onSubmitSuccess,
}: CustomActionFormProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [feedback, setFeedback] = useState<string>("")
  const [loading, setLoading] = useState<boolean>(false)
  const [persuaderId, setPersuaderId] = useState<string>("")
  const [targetId, setTargetId] = useState<string>("")
  const [talents, setBribe] = useState<number>(0)

  const myFactionId = availableAction.faction

  const persuadingCandidates = publicGameState.senators
    .filter(
      (s) => s.alive && s.location === "Rome" && s.faction === myFactionId,
    )
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const targetCandidates = publicGameState.senators
    .filter(
      (s) =>
        s.alive &&
        s.location === "Rome" &&
        (s.faction === null ||
          (s.faction !== myFactionId && !s.titles.includes(FACTION_LEADER))),
    )
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const persuader = publicGameState.senators.find(
    (s) => String(s.id) === persuaderId,
  )
  const target = publicGameState.senators.find((s) => String(s.id) === targetId)

  const maxBribe = persuader?.talents ?? 0
  const modifier =
    persuader && target
      ? persuader.oratory +
        persuader.influence +
        talents -
        target.loyalty -
        target.talents -
        (target.faction ? 7 : 0)
      : 0

  useEffect(() => {
    setBribe(0)
  }, [persuaderId])

  const openDialog = () => {
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
      dialogRef.current?.showModal()
    }
  }, [isExpanded])

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!publicGameState.game || !persuader || !target) return
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
        body: JSON.stringify({
          Persuader: String(persuader.id),
          Target: String(target.id),
          Talents: String(talents),
        }),
      },
    )
    setLoading(false)
    if (response.ok) {
      setPersuaderId("")
      setTargetId("")
      setBribe(0)
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
        Attempt persuasion...
      </button>

      <dialog
        ref={dialogRef}
        onClose={handleDialogClose}
        className="min-w-80 rounded-lg bg-white p-6 shadow-lg"
      >
        <div className="flex flex-col gap-6">
          <div className="flex w-0 min-w-full flex-col gap-4">
            <h3 className="text-xl">Attempt persuasion</h3>
            <p>
              You may attempt to persuade any non-faction leader senator to join
              your faction.
            </p>
            <p className="text-sm">
              Senators with high oratory and influence make excellent
              persuaders, while those with low loyalty make the easiest targets.
              Optionally give the target a bribe to increase your chance of
              success.
            </p>
          </div>
          {feedback && (
            <div className="inline-flex rounded-md bg-red-50 px-2 py-1 text-red-600">
              <p>{feedback}</p>
            </div>
          )}
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-1">
              <label className="font-semibold">Persuader</label>
              <select
                value={persuaderId}
                onChange={(e) => setPersuaderId(e.target.value)}
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select an option --</option>
                {persuadingCandidates.map((s) => (
                  <option key={s.id} value={String(s.id)}>
                    {s.displayName}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-semibold">Target</label>
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select an option --</option>
                {targetCandidates.map((s) => (
                  <option key={s.id} value={String(s.id)}>
                    {s.displayName}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <PersuasionPanel
            bribe={talents}
            setBribe={setBribe}
            maxBribe={maxBribe}
            modifier={modifier}
            threshold={10}
            label="Bribe"
            alwaysShowBribeInput
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
              disabled={loading}
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

export default AttemptPersuasionForm
