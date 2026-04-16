"use client"

import Fleet from "@/classes/Fleet"
import Legion from "@/classes/Legion"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import { toSentenceCase } from "@/helpers/text"
import useCustomActionForm from "@/hooks/useCustomActionForm"

import ActionDescription from "../ActionDescription"
import { CustomActionFormProps } from "../ActionDispatcher"

const ProposeDeployingForcesForm = ({
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

  // Build eligible commanders from publicGameState
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

  const availableLegions: Legion[] = publicGameState.legions
    .filter((l: Legion) => l.campaign === null)
    .sort((a: Legion, b: Legion) => a.number - b.number)

  const availableFleets: Fleet[] = publicGameState.fleets
    .filter((f: Fleet) => f.campaign === null)
    .sort((a: Fleet, b: Fleet) => a.number - b.number)

  const wars: War[] = [...publicGameState.wars].sort(
    (a: War, b: War) => a.id - b.id,
  )

  const selectedCommanderId = selection["Commander"]
    ? Number(selection["Commander"])
    : null
  const selectedCommander = selectedCommanderId
    ? publicGameState.senators.find(
        (s: Senator) => s.id === selectedCommanderId,
      )
    : null
  const isDictator = selectedCommander?.titles?.includes("Dictator") ?? false
  const masterOfHorse = isDictator
    ? publicGameState.senators.find((s: Senator) =>
        s.titles?.includes("Master of Horse"),
      )
    : null

  const toggleUnit = (fieldName: string, id: number) => {
    const current = (selection[fieldName] ?? []) as number[]
    const next = current.includes(id)
      ? current.filter((v) => v !== id)
      : [...current, id]
    setSelection((prev) => ({ ...(prev ?? {}), [fieldName]: next }))
  }

  const selectAll = (fieldName: string, ids: number[]) => {
    setSelection((prev) => ({ ...(prev ?? {}), [fieldName]: ids }))
  }

  const selectNone = (fieldName: string) => {
    setSelection((prev) => ({ ...(prev ?? {}), [fieldName]: [] }))
  }

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault()
    await submit(selection as object)
  }

  const selectedLegions = (selection["Legions"] ?? []) as number[]
  const selectedFleets = (selection["Fleets"] ?? []) as number[]

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
            {/* Commander select */}
            <div className="flex flex-col gap-2">
              <div className="flex flex-col gap-1">
                <label className="font-semibold">Commander</label>
                <select
                  value={(selection["Commander"] as string) ?? ""}
                  onChange={(e) =>
                    setSelection((prev) => ({
                      ...(prev ?? {}),
                      Commander: e.target.value,
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
              {isDictator && masterOfHorse && (
                <div className="flex w-0 min-w-full rounded-md text-sm">
                  The Dictator will be joined by the Master of Horse
                </div>
              )}
            </div>

            {/* Target war select */}
            <div className="flex flex-col gap-1">
              <label className="font-semibold">Target war</label>
              <select
                value={(selection["Target war"] as string) ?? ""}
                onChange={(e) =>
                  setSelection((prev) => ({
                    ...(prev ?? {}),
                    "Target war": e.target.value,
                  }))
                }
                required
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select an option --</option>
                {wars.map((war) => (
                  <option key={war.id} value={war.id}>
                    {toSentenceCase(war.name)}
                  </option>
                ))}
              </select>
            </div>

            {/* Legions + Fleets inline (side-by-side on sm+) */}
            <div className="flex flex-col gap-6 sm:flex-row">
              <div className="flex flex-1 flex-col gap-1">
                <label className="font-semibold">Legions</label>
                <div className="flex flex-col gap-1 overflow-hidden rounded-md border border-blue-600">
                  <div className="inline-block w-full min-w-[180px] select-none px-2 pt-1 text-sm">
                    Selected: {selectedLegions.length}{" "}
                    <span className="text-neutral-600">/</span>{" "}
                    <button
                      type="button"
                      onClick={() =>
                        selectAll(
                          "Legions",
                          availableLegions.map((l) => l.id),
                        )
                      }
                      className="text-blue-600 hover:underline"
                    >
                      All
                    </button>{" "}
                    <span className="text-neutral-600">/</span>{" "}
                    <button
                      type="button"
                      onClick={() => selectNone("Legions")}
                      className="text-blue-600 hover:underline"
                    >
                      None
                    </button>
                  </div>
                  <div className="flex max-h-48 flex-col gap-x-4 gap-y-1 overflow-auto pb-1 pl-2.5">
                    {availableLegions.map((legion) => (
                      <label
                        key={legion.id}
                        className="inline-flex items-center gap-2 whitespace-nowrap"
                      >
                        <input
                          type="checkbox"
                          checked={selectedLegions.includes(legion.id)}
                          onChange={() => toggleUnit("Legions", legion.id)}
                          className="rounded border-blue-600"
                        />
                        <span className="inline-block pr-4">
                          Legion {toSentenceCase(legion.name)}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex flex-1 flex-col gap-1">
                <label className="font-semibold">Fleets</label>
                <div className="flex flex-col gap-1 overflow-hidden rounded-md border border-blue-600">
                  <div className="inline-block w-full min-w-[180px] select-none px-2 pt-1 text-sm">
                    Selected: {selectedFleets.length}{" "}
                    <span className="text-neutral-600">/</span>{" "}
                    <button
                      type="button"
                      onClick={() =>
                        selectAll(
                          "Fleets",
                          availableFleets.map((f) => f.id),
                        )
                      }
                      className="text-blue-600 hover:underline"
                    >
                      All
                    </button>{" "}
                    <span className="text-neutral-600">/</span>{" "}
                    <button
                      type="button"
                      onClick={() => selectNone("Fleets")}
                      className="text-blue-600 hover:underline"
                    >
                      None
                    </button>
                  </div>
                  <div className="flex max-h-48 flex-col gap-x-4 gap-y-1 overflow-auto pb-1 pl-2.5">
                    {availableFleets.map((fleet) => (
                      <label
                        key={fleet.id}
                        className="inline-flex items-center gap-2 whitespace-nowrap"
                      >
                        <input
                          type="checkbox"
                          checked={selectedFleets.includes(fleet.id)}
                          onChange={() => toggleUnit("Fleets", fleet.id)}
                          className="rounded border-blue-600"
                        />
                        <span className="inline-block pr-4">
                          Fleet {toSentenceCase(fleet.name)}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
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

export default ProposeDeployingForcesForm
