"use client"

import Campaign from "@/classes/Campaign"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import { toSentenceCase } from "@/helpers/text"
import useCustomActionForm from "@/hooks/useCustomActionForm"

import ActionDescription from "../ActionDescription"
import { CustomActionFormProps } from "../ActionDispatcher"

const ProposeReplacingProconsulForm = ({
  availableAction,
  publicGameState,
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

  // Replaceable campaigns: those commanded by a Proconsul
  const proconsulIds = new Set(
    publicGameState.senators
      .filter((s: Senator) => s.titles.includes("Proconsul"))
      .map((s: Senator) => s.id),
  )
  const replaceableCampaigns: Campaign[] = publicGameState.campaigns
    .filter(
      (c: Campaign) => c.commander !== null && proconsulIds.has(c.commander),
    )
    .sort((a: Campaign, b: Campaign) => a.id - b.id)

  // Build eligible replacement commanders from publicGameState
  const mohExists = publicGameState.senators.some((s: Senator) =>
    s.titles.includes("Master of Horse"),
  )
  let availableCommanders: Senator[] = publicGameState.senators
    .filter(
      (s: Senator) =>
        s.alive &&
        s.faction !== null &&
        s.location === "Rome" &&
        (s.titles.includes("Rome Consul") ||
          s.titles.includes("Field Consul") ||
          (s.titles.includes("Dictator") && mohExists)),
    )
    .sort((a: Senator, b: Senator) => a.familyName.localeCompare(b.familyName))

  // Field Consul ordering restriction (consuls only, Dictator is exempt)
  const fieldConsuls = availableCommanders.filter((s: Senator) =>
    s.titles.includes("Field Consul"),
  )
  if (fieldConsuls.length === 1 && fieldConsuls[0].location === "Rome") {
    availableCommanders = availableCommanders.filter(
      (s: Senator) => !s.titles.includes("Rome Consul"),
    )
  }

  const selectedReplacementId = selection["Replacement commander"]
    ? Number(selection["Replacement commander"])
    : null
  const selectedReplacement = selectedReplacementId
    ? publicGameState.senators.find(
        (s: Senator) => s.id === selectedReplacementId,
      )
    : null
  const isDictator = selectedReplacement?.titles?.includes("Dictator") ?? false
  const masterOfHorse = isDictator
    ? publicGameState.senators.find((s: Senator) =>
        s.titles?.includes("Master of Horse"),
      )
    : null

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    await submit(selection as object)
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
        className="min-w-80 rounded-lg bg-white p-6 shadow-lg"
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
            {/* Campaign select */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold">Campaign</label>
              <select
                value={(selection["Campaign"] as string) ?? ""}
                onChange={(e) =>
                  setSelection((prev) => ({
                    ...(prev ?? {}),
                    Campaign: e.target.value,
                  }))
                }
                required
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select an option --</option>
                {replaceableCampaigns.map((campaign) => {
                  const war = publicGameState.wars.find(
                    (w: War) => w.id === campaign.war,
                  )
                  return (
                    <option key={campaign.id} value={campaign.id}>
                      {toSentenceCase(campaign.displayName)} (
                      {toSentenceCase(war?.name ?? "")})
                    </option>
                  )
                })}
              </select>
            </div>

            {/* Replacement commander select */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold">Replacement commander</label>
              <select
                value={(selection["Replacement commander"] as string) ?? ""}
                onChange={(e) =>
                  setSelection((prev) => ({
                    ...(prev ?? {}),
                    "Replacement commander": e.target.value,
                  }))
                }
                required
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select an option --</option>
                {availableCommanders.map((senator) => (
                  <option key={senator.id} value={senator.id}>
                    {toSentenceCase(senator.displayName)}
                  </option>
                ))}
              </select>
            </div>

            {/* MoH info banner (when Dictator selected as replacement) */}
            {isDictator && masterOfHorse && (
              <div className="flex w-0 min-w-full rounded-md text-sm">
                The Dictator will be joined by the Master of Horse
              </div>
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

export default ProposeReplacingProconsulForm
