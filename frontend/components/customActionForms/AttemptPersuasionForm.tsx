"use client"

import { useEffect } from "react"

import Senator from "@/classes/Senator"
import useCustomActionForm from "@/hooks/useCustomActionForm"

import { CustomActionFormProps } from "../ActionDispatcher"
import Checkbox from "../Checkbox"
import PersuasionPanel from "./sharedPanels/PersuasionPanel"

const FACTION_LEADER = "faction leader"

const AttemptPersuasionForm = ({
  availableAction,
  publicGameState,
  privateGameState,
  selection,
  setSelection,
  isExpanded,
  setIsExpanded,
  onSubmitSuccess,
}: CustomActionFormProps) => {
  const { dialogRef, feedback, loading, openDialog, closeDialog, handleDialogClose, submit } =
    useCustomActionForm({ availableAction, publicGameState, isExpanded, setIsExpanded, onSubmitSuccess })

  const persuaderId = (selection["Persuader"] as string) ?? ""
  const targetId = (selection["Target"] as string) ?? ""
  const talents = parseInt((selection["Talents"] as string) ?? "0")

  const setPersuaderId = (id: string) =>
    setSelection((prev) => ({ ...(prev ?? {}), Persuader: id }))
  const setTargetId = (id: string) =>
    setSelection((prev) => ({ ...(prev ?? {}), Target: id }))
  const setBribe = (value: number) =>
    setSelection((prev) => ({ ...(prev ?? {}), Talents: String(value) }))

  const hasSeduction =
    privateGameState.faction?.cards.includes("seduction") ?? false
  const hasBlackmail =
    privateGameState.faction?.cards.includes("blackmail") ?? false

  const useSeduction = (selection["Seduction"] as boolean) ?? false
  const useBlackmail = (selection["Blackmail"] as boolean) ?? false

  const myFactionId = availableAction.faction

  const allPersuaders = publicGameState.senators
    .filter(
      (s) => s.alive && s.location === "Rome" && s.faction === myFactionId,
    )
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const allTargets = publicGameState.senators
    .filter(
      (s) =>
        s.alive &&
        s.location === "Rome" &&
        (s.faction === null ||
          (s.faction !== myFactionId && !s.titles.includes(FACTION_LEADER))),
    )
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const isPossible = (persuader: Senator, target: Senator) =>
    persuader.oratory +
      persuader.influence +
      persuader.talents -
      target.loyalty -
      target.talents -
      (target.faction ? 7 : 0) >=
    2

  const persuader = publicGameState.senators.find(
    (s) => String(s.id) === persuaderId,
  )
  const target = publicGameState.senators.find((s) => String(s.id) === targetId)

  const persuadingCandidates = target
    ? allPersuaders.filter((p) => isPossible(p, target))
    : allPersuaders.filter((p) => allTargets.some((t) => isPossible(p, t)))
  const targetCandidates = persuader
    ? allTargets.filter((t) => isPossible(persuader, t))
    : allTargets.filter((t) => allPersuaders.some((p) => isPossible(p, t)))

  const threshold = publicGameState.game?.eraEnds ? 9 : 10
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
  const isZeroChance = !!persuader && !!target && modifier < 2

  useEffect(() => {
    setBribe(0)
    if (persuader && target && !isPossible(persuader, target)) {
      setTargetId("")
    }
  }, [persuaderId])

  useEffect(() => {
    if (persuader && target && !isPossible(persuader, target)) {
      setPersuaderId("")
      setBribe(0)
    }
  }, [targetId])

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!persuader || !target) return
    await submit({
      Persuader: String(persuader.id),
      Target: String(target.id),
      Talents: String(talents),
      Seduction: useSeduction,
      Blackmail: useBlackmail,
    })
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
            threshold={threshold}
            label="Bribe"
            alwaysShowBribeInput
          />
          {(hasSeduction || hasBlackmail) && (
            <div className="flex w-0 min-w-full flex-col gap-2">
              {hasSeduction && (
                <Checkbox
                  checked={useSeduction}
                  disabled={useBlackmail}
                  onChange={(checked) =>
                    setSelection((prev) => ({
                      ...(prev ?? {}),
                      Seduction: checked,
                      Blackmail: false,
                    }))
                  }
                >
                  Use <strong>seduction</strong> to prevent counter-bribes
                </Checkbox>
              )}
              {hasBlackmail && (
                <Checkbox
                  checked={useBlackmail}
                  disabled={useSeduction}
                  onChange={(checked) =>
                    setSelection((prev) => ({
                      ...(prev ?? {}),
                      Blackmail: checked,
                      Seduction: false,
                    }))
                  }
                >
                  Use <strong>blackmail</strong> to prevent counter-bribes and
                  tarnish the target&apos;s reputation if the persuasion is
                  unsuccessful
                </Checkbox>
              )}
            </div>
          )}
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
              disabled={loading || !persuader || !target || isZeroChance}
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

export default AttemptPersuasionForm
