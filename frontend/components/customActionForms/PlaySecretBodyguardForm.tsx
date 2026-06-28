"use client"

import useCustomActionForm from "@/hooks/useCustomActionForm"

import { CustomActionFormProps } from "../ActionBar"
import ActionDescription from "../ActionDescription"

const outcomeLabel = (result: number): string => {
  if (result <= 2) return "Assassin is caught and executed"
  if (result <= 4) return "Target survives"
  return "Target is assassinated"
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

  const bodyguardCardCount =
    privateGameState.faction?.cards.filter((c) => c === "secret bodyguard")
      .length ?? 0

  const count = parseInt(
    (selection["Secret bodyguards to play"] as string) ?? "1",
  )

  const setCount = (val: number) => {
    const clamped = Math.max(1, Math.min(bodyguardCardCount, val))
    setSelection((prev) => ({
      ...(prev ?? {}),
      "Secret bodyguards to play": String(clamped),
    }))
  }

  const currentRoll = publicGameState.game?.assassinationRollResult ?? 0
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

          <div className="flex w-0 min-w-full flex-col gap-6">
            {/* Cards to play */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold">
                Secret bodyguard cards to play
              </label>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setCount(count - 1)}
                    disabled={count <= 1}
                    className="relative h-6 min-w-6 rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                  >
                    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                      &minus;
                    </div>
                  </button>
                  <input
                    type="number"
                    min={1}
                    max={bodyguardCardCount}
                    value={count}
                    onChange={(e) => setCount(parseInt(e.target.value) || 1)}
                    className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5"
                  />
                  <button
                    type="button"
                    onClick={() => setCount(count + 1)}
                    disabled={count >= bodyguardCardCount}
                    className="relative h-6 min-w-6 rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-transparent"
                  >
                    <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                      +
                    </div>
                  </button>
                </div>
                {bodyguardCardCount > 1 && (
                  <div className="flex w-full items-center justify-center">
                    <button
                      type="button"
                      className={`w-10 cursor-default px-2 text-sm ${count !== 1 && "text-neutral-400"}`}
                      onClick={() => setCount(1)}
                    >
                      1
                    </button>
                    <input
                      type="range"
                      min={1}
                      max={bodyguardCardCount}
                      value={count}
                      onChange={(e) => setCount(Number(e.target.value))}
                      className="w-full"
                    />
                    <button
                      type="button"
                      className={`w-10 cursor-default px-2 text-sm ${count !== bodyguardCardCount && "text-neutral-400"}`}
                      onClick={() => setCount(bodyguardCardCount)}
                    >
                      {bodyguardCardCount}
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Outcome */}
            <div className="flex flex-col gap-4 text-sm">
              <div>
                <p className="font-semibold">Without bodyguards:</p>
                <ul className="ml-10 list-disc">
                  <li>{outcomeLabel(currentRoll)}</li>
                </ul>
              </div>
              <div>
                <p className="font-semibold">
                  With {count} bodyguard{count !== 1 ? "s" : ""}:
                </p>
                <ul className="ml-10 list-disc">
                  <li>{outcomeLabel(modifiedRoll)}</li>
                  {modifiedRoll > 2 && (
                    <li>
                      {" "}
                      {count} chance{count !== 1 ? "s" : ""} to catch the
                      assassin
                    </li>
                  )}
                </ul>
              </div>
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
