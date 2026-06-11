"use client"

import Senator from "@/classes/Senator"
import useCustomActionForm from "@/hooks/useCustomActionForm"
import ActionDescription from "../ActionDescription"

import { CustomActionFormProps } from "../ActionDispatcher"

const PressureKnightsForm = ({
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

  const ownSenators: Senator[] = publicGameState.senators
    .filter((s) => s.faction === factionId && s.alive && s.knights > 0)
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const pressures = (selection["Pressures"] ?? {}) as { [id: string]: number }

  const getSenatorValue = (senator: Senator) =>
    pressures[String(senator.id)] ?? 0

  const totalPressured = ownSenators.reduce(
    (sum, s) => sum + getSenatorValue(s),
    0
  )

  const updateSenator = (senator: Senator, newValue: number) => {
    const id = String(senator.id)
    const clamped = Math.max(0, Math.min(newValue, senator.knights))

    setSelection((prev) => ({
      ...(prev ?? {}),
      Pressures: {
        ...((prev?.["Pressures"] ?? {}) as { [id: string]: number }),
        [id]: clamped,
      },
    }))
  }

  const handleReset = () => {
    const resetPressures: { [id: string]: number } = {}
    ownSenators.forEach((s) => {
      resetPressures[String(s.id)] = 0
    })
    setSelection((prev) => ({ ...(prev ?? {}), Pressures: resetPressures }))
  }

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    const payload: { [id: string]: number } = {}
    ownSenators.forEach((s) => {
      payload[String(s.id)] = getSenatorValue(s)
    })
    await submit({ Pressures: payload })
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
        className="min-w-[28rem] rounded-lg bg-white p-6 shadow-lg"
        onClose={handleDialogClose}
      >
        <div className="flex flex-col gap-6">
          <div className="flex w-0 min-w-full flex-col gap-4">
            <h3 className="text-xl">{availableAction.name}</h3>
            <ActionDescription
              actionName={availableAction.name}
              context={availableAction.context}
            />
            <p className="text-sm text-neutral-600">
              Choose how many knights to pressure under each of your senators.
              You will receive one die roll in Talents per pressured knight,
              but the knights are lost.
            </p>
          </div>

          {feedback && (
            <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">
              {feedback}
            </div>
          )}

          {ownSenators.length === 0 ? (
            <p className="text-sm text-neutral-500">
              You have no knights available to pressure.
            </p>
          ) : (
            <div className="flex flex-col gap-4">
              {ownSenators.map((senator) => {
                const current = getSenatorValue(senator)
                const max = senator.knights

                return (
                  <div
                    key={senator.id}
                    className="flex items-center justify-between gap-4"
                  >
                    <label className="text-sm">
                      {senator.displayName}{" "}
                      <span className="text-neutral-500">(max {max})</span>
                    </label>

                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => updateSenator(senator, current - 1)}
                          disabled={current <= 0}
                          className="relative h-6 min-w-6 rounded-full border border-red-600 text-red-600 hover:bg-red-100 disabled:border-neutral-300 disabled:text-neutral-400"
                        >
                          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                            &minus;
                          </div>
                        </button>
                        <input
                          type="number"
                          min={0}
                          max={max}
                          value={current}
                          onChange={(e) =>
                            updateSenator(senator, Number(e.target.value))
                          }
                          className="w-[70px] rounded-md border border-blue-600 p-1 px-1.5 text-center"
                        />
                        <button
                          type="button"
                          onClick={() => updateSenator(senator, current + 1)}
                          disabled={current >= max}
                          className="relative h-6 min-w-6 rounded-full border border-green-600 text-green-600 hover:bg-green-100 disabled:border-neutral-300 disabled:text-neutral-400"
                        >
                          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                            +
                          </div>
                        </button>
                      </div>

                      <input
                        type="range"
                        min={0}
                        max={max}
                        value={current}
                        onChange={(e) =>
                          updateSenator(senator, Number(e.target.value))
                        }
                        className="w-24 sm:w-32"
                      />

                      <div className="w-6 text-right text-sm tabular-nums text-neutral-600">
                        {current}
                      </div>
                    </div>
                  </div>
                )
              })}

              <div className="mt-2 border-t pt-3 text-sm text-neutral-600">
                Total knights to pressure:{" "}
                <span className="font-medium text-neutral-800">
                  {totalPressured}
                </span>
              </div>
            </div>
          )}

          <div className="mt-4 flex justify-end gap-3">
            <button
              type="button"
              onClick={closeDialog}
              className="rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
              disabled={loading || ownSenators.length === 0}
            >
              Reset
            </button>
            <button
              type="submit"
              className="rounded-md border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:border-neutral-300 disabled:text-neutral-400"
              disabled={loading || ownSenators.length === 0}
            >
              {loading ? "Submitting..." : "Confirm"}
            </button>
          </div>
        </div>
      </dialog>
    </form>
  )
}

export default PressureKnightsForm
