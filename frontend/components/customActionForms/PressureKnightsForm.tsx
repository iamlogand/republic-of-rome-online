"use client"

import Senator from "@/classes/Senator"
import { getEvilOmensLevel } from "@/helpers/gameEffects"
import useCustomActionForm from "@/hooks/useCustomActionForm"

import { CustomActionFormProps } from "../ActionBar"
import ActionDescription from "../ActionDescription"
import NumberInput from "../NumberInput"

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

  const evilOmensLevel = getEvilOmensLevel(publicGameState.game?.effects ?? [])

  const ownSenators: Senator[] = publicGameState.senators
    .filter((s) => s.faction === factionId && s.alive && s.knights > 0)
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const pressures = (selection["Pressures"] ?? {}) as { [id: string]: number }

  const getSenatorValue = (senator: Senator) =>
    pressures[String(senator.id)] ?? 0

  const totalPressured = ownSenators.reduce(
    (sum, s) => sum + getSenatorValue(s),
    0,
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
              Each pressured knight yields up to{" "}
              {Math.max(0, 6 - evilOmensLevel)} talents
              {evilOmensLevel > 0 ? " (reduced by evil omens)" : ""}.
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
                  <NumberInput
                    key={senator.id}
                    label={senator.displayName}
                    value={current}
                    onChange={(v) => updateSenator(senator, v)}
                    min={0}
                    max={max}
                  />
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
