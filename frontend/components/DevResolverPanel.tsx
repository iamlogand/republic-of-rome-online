"use client"

import { forwardRef, useImperativeHandle, useRef, useState } from "react"

import getCSRFToken from "@/helpers/csrf"

interface ResolverConfig {
  dice_rolls: number[]
  casualty_order: string[]
  mortality_chits: string[]
}

interface Props {
  gameId: number
}

export interface DevResolverPanelHandle {
  open: () => void
}

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_ORIGIN

const DevResolverPanel = forwardRef<DevResolverPanelHandle, Props>(
  function DevResolverPanel({ gameId }, ref) {
    const dialogRef = useRef<HTMLDialogElement>(null)
    const [diceRolls, setDiceRolls] = useState("")
    const [casualtyOrder, setCasualtyOrder] = useState("")
    const [mortalityChits, setMortalityChits] = useState("")
    const [pending, setPending] = useState<ResolverConfig | null>(null)
    const [saving, setSaving] = useState(false)

    const fetchPending = async () => {
      const res = await fetch(`${BACKEND}/api/test/resolver/${gameId}/`, {
        credentials: "include",
      })
      if (!res.ok) return
      const data = await res.json()
      setPending(data.resolver ?? null)
    }

    useImperativeHandle(ref, () => ({
      open: () => {
        fetchPending()
        dialogRef.current?.showModal()
      },
    }))

    const parseIntegers = (raw: string): number[] =>
      raw
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .map(Number)
        .filter((n) => !isNaN(n))

    const parseStrings = (raw: string): string[] =>
      raw
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)

    const handleSet = async () => {
      setSaving(true)
      const config: ResolverConfig = {
        dice_rolls: parseIntegers(diceRolls),
        casualty_order: parseStrings(casualtyOrder),
        mortality_chits: parseStrings(mortalityChits),
      }
      const res = await fetch(`${BACKEND}/api/test/resolver/${gameId}/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(config),
      })
      if (res.ok) setPending(config)
      setSaving(false)
    }

    const handleClear = async () => {
      await fetch(`${BACKEND}/api/test/resolver/${gameId}/`, {
        method: "DELETE",
        credentials: "include",
        headers: { "X-CSRFToken": getCSRFToken() },
      })
      setPending(null)
    }

    const handleClose = () => {
      dialogRef.current?.close()
    }

    return (
      <dialog
        ref={dialogRef}
        className="rounded-lg bg-white p-6 shadow-lg"
        onClick={(e) => {
          if (e.target === dialogRef.current) handleClose()
        }}
      >
        <div className="flex w-80 flex-col gap-4">
          <h2 className="text-lg font-semibold">Dev: Random Resolver</h2>

          {pending ? (
            <div className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm">
              <p className="font-medium text-amber-800">Resolver pending</p>
              <p className="text-amber-700">
                Dice: [{pending.dice_rolls.join(", ")}]
              </p>
              {pending.casualty_order.length > 0 && (
                <p className="text-amber-700">
                  Casualties: [{pending.casualty_order.join(", ")}]
                </p>
              )}
              {pending.mortality_chits.length > 0 && (
                <p className="text-amber-700">
                  Chits: [{pending.mortality_chits.join(", ")}]
                </p>
              )}
            </div>
          ) : (
            <p className="text-sm text-neutral-500">No resolver pending</p>
          )}

          <div className="flex flex-col gap-3">
            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium">
                Dice rolls (comma-separated integers)
              </span>
              <input
                type="text"
                value={diceRolls}
                onChange={(e) => setDiceRolls(e.target.value)}
                placeholder="e.g. 6, 6, 3"
                className="rounded border border-neutral-300 px-2 py-1 text-sm"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium">
                Casualty order (unit names, first = first destroyed)
              </span>
              <input
                type="text"
                value={casualtyOrder}
                onChange={(e) => setCasualtyOrder(e.target.value)}
                placeholder="e.g. Legion 1, Fleet 2"
                className="rounded border border-neutral-300 px-2 py-1 text-sm"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium">
                Mortality chits (senator codes or &quot;none&quot;)
              </span>
              <input
                type="text"
                value={mortalityChits}
                onChange={(e) => setMortalityChits(e.target.value)}
                placeholder="e.g. 1, none, 7"
                className="rounded border border-neutral-300 px-2 py-1 text-sm"
              />
            </label>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleSet}
              disabled={saving}
              className="rounded border border-blue-600 px-4 py-1 text-blue-600 hover:bg-blue-50 disabled:border-neutral-300 disabled:text-neutral-400"
            >
              {saving ? "Saving…" : "Set"}
            </button>
            {pending && (
              <button
                onClick={handleClear}
                className="rounded border border-neutral-400 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
              >
                Clear
              </button>
            )}
            <button
              onClick={handleClose}
              className="ml-auto rounded border border-neutral-300 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
            >
              Close
            </button>
          </div>
        </div>
      </dialog>
    )
  },
)

export default DevResolverPanel
