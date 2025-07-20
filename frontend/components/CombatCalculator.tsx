import { Dispatch, SetStateAction, useEffect, useRef, useState } from "react"
import React from "react"

import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import getDiceProbability from "@/utils/dice"

interface ActionHandlerProps {
  publicGameState: PublicGameState
}

const CombatCalculator = ({ publicGameState }: ActionHandlerProps) => {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [commander, setCommander] = useState<Senator | null>(null)
  const [war, setWar] = useState<War | null>(null)
  const [battle, setBattle] = useState<"Land" | "Naval">("Land")
  const [legions, setLegions] = useState<number>(0)
  const [veteranLegions, setVeteranLegions] = useState<number>(0)
  const [fleets, setFleets] = useState<number>(0)

  const openDialog = () => {
    dialogRef.current?.showModal()
  }

  const closeDialog = () => {
    dialogRef.current?.close()
  }

  // Auto select land battle if selected war has no naval strength
  useEffect(() => {
    if (war?.navalStrength === 0) setBattle("Land")
  }, [war])

  const renderNumberField = (
    name: string,
    state: number,
    setState: Dispatch<SetStateAction<number>>,
  ) => {
    const min = 0
    const max = 25
    return (
      <div className="flex max-w-[350px] flex-col gap-1">
        <label htmlFor={name} className="font-semibold">
          {name}
        </label>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                setState((prev: number) =>
                  Number(prev) > max ? max : Number(prev) - 1,
                )
              }}
              disabled={Number(state) <= min}
              className="relative h-6 min-w-6 rounded-full border border-red-500 text-red-500 hover:bg-red-100 disabled:border-neutral-400 disabled:text-neutral-400 disabled:hover:bg-transparent"
            >
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                &minus;
              </div>
            </button>
            <input
              id={name}
              type="number"
              min={min}
              max={max}
              value={state}
              onChange={(e) => setState(Number(e.target.value))}
              required
              className="w-[80px] rounded-md border border-blue-600 p-1 px-1.5"
            />
            <button
              type="button"
              onClick={() => {
                setState((prev) =>
                  Number(prev) < min ? min : Number(prev) + 1,
                )
              }}
              disabled={Number(state) >= max}
              className="relative h-6 min-w-6 rounded-full border border-green-500 text-green-500 hover:bg-green-100 disabled:border-neutral-400 disabled:text-neutral-400 disabled:hover:bg-transparent"
            >
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 select-none text-xl">
                +
              </div>
            </button>
          </div>
          <div className="flex w-full items-center justify-center">
            <button
              type="button"
              className={`w-10 cursor-default px-2 text-sm ${
                state !== min && "text-neutral-400"
              }`}
              onClick={() => setState(min)}
            >
              {min}
            </button>

            <input
              type="range"
              min={min}
              max={max}
              value={state}
              onChange={(e) => setState(Number(e.target.value))}
              className="w-full"
            ></input>
            <button
              type="button"
              className={`w-10 cursor-default px-2 text-sm ${
                state !== max && "text-neutral-400"
              }`}
              onClick={() => setState(max)}
            >
              {max}
            </button>
          </div>
        </div>
      </div>
    )
  }

  const forceStrength =
    (commander?.military ?? 0) +
    (battle === "Land" ? legions + veteranLegions * 2 : fleets)
  const warStrength =
    (battle === "Land" ? war?.landStrength : war?.navalStrength) ?? 0
  const modifier = forceStrength - warStrength

  const victoryProbability = Math.round(
    getDiceProbability(
      3,
      modifier,
      {
        min: 14,
      },
      [...(war?.standoffNumbers ?? []), ...(war?.disasterNumbers ?? [])],
    ) * 100,
  )

  const stalemateProbability = Math.round(
    getDiceProbability(
      3,
      modifier,
      {
        min: 8,
        max: 13,
      },
      [...(war?.standoffNumbers ?? []), ...(war?.disasterNumbers ?? [])],
    ) * 100,
  )

  const defeatProbability = Math.round(
    getDiceProbability(
      3,
      modifier,
      {
        max: 7,
      },
      [...(war?.standoffNumbers ?? []), ...(war?.disasterNumbers ?? [])],
    ) * 100,
  )

  const standoffProbability = Math.round(
    getDiceProbability(3, 0, {
      exacts: war?.standoffNumbers,
    }) * 100,
  )

  const disasterProbability = Math.round(
    getDiceProbability(3, 0, {
      exacts: war?.disasterNumbers,
    }) * 100,
  )

  return (
    <>
      <button
        type="button"
        onClick={openDialog}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        Combat Calculator
      </button>
      <dialog ref={dialogRef} className="rounded-lg bg-white p-6 shadow-lg">
        <h3 className="text-xl">Combat Calculator</h3>
        <div className="flex flex-row gap-12 py-6">
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-1">
              <label htmlFor="commander" className="font-semibold">
                Commander{" "}
                <span className="text-sm font-normal text-neutral-600">
                  (military skill)
                </span>
              </label>
              <select
                id="commander"
                value={commander?.id}
                onChange={(e) => {
                  setCommander(
                    publicGameState.senators.find(
                      (s: Senator) => s.id.toString() === e.target.value,
                    ) ?? null,
                  )
                }}
                required
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select an option --</option>
                {publicGameState.senators?.map(
                  (senator: Senator, index: number) => (
                    <option key={index} value={senator.id}>
                      <>
                        {senator?.displayName} ({senator.military})
                      </>
                    </option>
                  ),
                )}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label htmlFor="war" className="font-semibold">
                Target war
              </label>
              <select
                id="war"
                value={war?.id}
                onChange={(e) => {
                  setWar(
                    publicGameState.wars.find(
                      (w: War) => w.id.toString() === e.target.value,
                    ) ?? null,
                  )
                }}
                required
                className="rounded-md border border-blue-600 p-1"
              >
                <option value="">-- select an option --</option>
                {publicGameState.wars?.map((war: War, index: number) => (
                  <option key={index} value={war.id}>
                    <>{war?.name}</>
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <button
                className={`select-none rounded-md border px-4 py-1 ${battle === "Land" ? "border-green-600 bg-green-200 text-green-900" : "border-neutral-400 text-neutral-500 hover:bg-neutral-100"}`}
                onClick={() => setBattle("Land")}
                disabled={battle === "Land"}
              >
                Land battle
              </button>
              {war?.navalStrength !== 0 && (
                <button
                  className={`select-none rounded-md border px-4 py-1 ${battle === "Naval" ? "border-blue-600 bg-blue-200 text-blue-900" : "border-neutral-400 text-neutral-500 hover:bg-neutral-100"}`}
                  onClick={() => setBattle("Naval")}
                  disabled={battle === "Naval"}
                >
                  Naval battle
                </button>
              )}
            </div>
            {renderNumberField("Legions", legions, setLegions)}
            {renderNumberField(
              "Veteran legions",
              veteranLegions,
              setVeteranLegions,
            )}
            {renderNumberField("Fleets", fleets, setFleets)}
          </div>
          <div className="flex w-[350px] flex-col items-start gap-6">
            <div className="flex flex-col items-start gap-1">
              <div className="font-semibold">Strengths</div>
              <div>Roman force strength: {forceStrength}</div>
              <div>War strength: {warStrength}</div>
            </div>
            <div className="flex flex-col items-start gap-1">
              <div className="font-semibold">Probabilities</div>
              <div className="flex gap-1">
                <div className="flex min-w-[135px] flex-col items-start gap-2">
                  <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                    Victory: {victoryProbability}%
                  </div>
                  <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                    Stalemate: {stalemateProbability}%
                  </div>
                  <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                    Defeat: {defeatProbability}%
                  </div>
                </div>
                <div className="flex min-w-[135px] flex-col items-start gap-2">
                  <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                    Disaster: {disasterProbability}%
                  </div>
                  <div className="rounded-md bg-neutral-100 px-2 py-1 text-neutral-600">
                    Standoff: {standoffProbability}%
                  </div>
                </div>
              </div>
            </div>
            {((war?.fleetSupport ?? 0) > fleets || modifier < 0) && (
              <div className="flex flex-col gap-1">
                <div className="font-semibold">Issues</div>
                <div className="flex flex-col gap-2 text-sm">
                  {(war?.fleetSupport ?? 0) > fleets && (
                    <>
                      <div className="rounded-md bg-red-50 px-2 py-1 text-red-600">
                        <strong className="font-semibold">
                          Insufficient fleet support
                        </strong>
                        : a minimum of {war?.fleetSupport} fleets are required
                        to prosecute this war
                      </div>
                    </>
                  )}
                  {modifier < 0 && (
                    <>
                      <div className="rounded-md bg-red-50 px-2 py-1 text-red-600">
                        <strong className="font-semibold">
                          Below minimum force
                        </strong>
                        : commander consent required to deploy a force below the
                        war strength
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-4">
          <button
            type="button"
            onClick={closeDialog}
            className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
          >
            Close
          </button>
        </div>
      </dialog>
    </>
  )
}

export default CombatCalculator
