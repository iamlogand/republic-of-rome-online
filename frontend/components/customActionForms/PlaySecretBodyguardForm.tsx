"use client"

import useCustomActionForm from "@/hooks/useCustomActionForm"

import ActionDescription from "../ActionDescription"
import { CustomActionFormProps } from "../ActionDispatcher"

const rollResultLabel = (result: number): string => {
  if (result <= 2) return "Caught — assassin is executed"
  if (result <= 4) return "No Effect — target survives"
  return "Killed — target is assassinated"
}

const rollResultColor = (result: number): string => {
  if (result <= 2) return "text-green-700"
  if (result <= 4) return "text-neutral-700"
  return "text-red-700"
}

const PlaySecretBodyguardForm = ({
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

  const currentRoll = publicGameState.game?.assassinationRollResult ?? 0

  const bodyguardCardCount = privateGameState.faction?.cards.filter(
    (c) => c === "secret bodyguard",
  ).length ?? 0

  const count = parseInt((selection["Secret bodyguards to play"] as string) ?? "1")
  const modifiedRoll = currentRoll - count

  const canSubmit = count >= 1 && count <= bodyguardCardCount

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!canSubmit) return
    await submit({ "Secret bodyguards to play": String(count) })
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

          <div className="flex flex-col gap-6">
            {/* Current roll result */}
            <div className="rounded-md border border-neutral-200 p-3">
              <p className="text-sm text-neutral-500">Current roll result</p>
              <p className="text-2xl font-bold">{currentRoll}</p>
              <p className={`text-sm font-medium ${rollResultColor(currentRoll)}`}>
                {rollResultLabel(currentRoll)}
              </p>
            </div>

            {/* Cards to play */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold">
                Secret Bodyguard cards to play{" "}
                <span className="font-normal text-neutral-500">
                  (1–{bodyguardCardCount} available)
                </span>
              </label>
              <input
                type="number"
                min={1}
                max={bodyguardCardCount}
                value={count}
                onChange={(e) => {
                  const val = Math.max(
                    1,
                    Math.min(bodyguardCardCount, parseInt(e.target.value) || 1),
                  )
                  setSelection((prev) => ({
                    ...(prev ?? {}),
                    "Secret bodyguards to play": String(val),
                  }))
                }}
                className="w-24 rounded-md border border-blue-600 p-1"
              />
            </div>

            {/* Modified roll preview */}
            <div className="rounded-md border border-blue-100 bg-blue-50 p-3">
              <p className="text-sm text-neutral-500">
                Modified result (after playing {count} card{count !== 1 ? "s" : ""})
              </p>
              <p className="text-2xl font-bold">{modifiedRoll}</p>
              <p className={`text-sm font-medium ${rollResultColor(modifiedRoll)}`}>
                {rollResultLabel(modifiedRoll)}
              </p>
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

export default PlaySecretBodyguardForm
