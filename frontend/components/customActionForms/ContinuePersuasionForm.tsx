"use client"

import useCustomActionForm from "@/hooks/useCustomActionForm"

import { CustomActionFormProps } from "../ActionDispatcher"
import PersuasionPanel from "./sharedPanels/PersuasionPanel"

const ContinuePersuasionForm = ({
  publicGameState,
  availableAction,
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

  const threshold = publicGameState.game?.eraEnds ? 9 : 10

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
  const maxAdditionalBribe = persuader?.talents ?? 0
  const talents = parseInt((selection["Talents"] as string) ?? "0")
  const modifier =
    persuader && target
      ? persuader.oratory +
        persuader.influence +
        2 * bribe +
        talents -
        target.loyalty -
        target.talents -
        (target.faction ? 7 : 0)
      : 0

  const setAdditionalBribe = (value: number) => {
    const clamped = Math.max(0, Math.min(maxAdditionalBribe, value))
    setSelection((prev) => ({
      ...(prev ?? {}),
      Talents: String(clamped),
    }))
  }

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    await submit(selection)
  }

  return (
    <form onSubmit={handleSubmit}>
      <button
        type="button"
        onClick={openDialog}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        Continue persuasion attempt...
      </button>

      <dialog
        ref={dialogRef}
        onClose={handleDialogClose}
        className="min-w-[24rem] rounded-lg bg-white p-6 shadow-lg"
      >
        <div className="flex flex-col gap-6">
          <div className="flex w-0 min-w-full flex-col gap-4">
            <h3 className="text-xl">Continue persuasion attempt</h3>
            <p>
              {persuader?.displayName} may resolve the persuasion attempt now or
              choose to give {target?.displayName} {bribe ? "another" : "a"}{" "}
              bribe.
            </p>
          </div>
          {feedback && (
            <div className="inline-flex rounded-md bg-red-50 px-2 py-1 text-red-600">
              <p>{feedback}</p>
            </div>
          )}
          <PersuasionPanel
            bribe={talents}
            setBribe={setAdditionalBribe}
            maxBribe={maxAdditionalBribe}
            modifier={modifier}
            threshold={threshold}
            label="Talents"
          />

          <div className="text-sm font-semibold">
            {talents === 0 ? (
              <span>The persuasion attempt will resolve immediately</span>
            ) : (
              <span>There will be another round of counter-bribes</span>
            )}
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
              disabled={loading}
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

export default ContinuePersuasionForm
