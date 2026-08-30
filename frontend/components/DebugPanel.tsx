"use client"

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react"
import useWebSocket from "react-use-websocket"

import getCSRFToken from "@/helpers/csrf"
import useIsMobile from "@/hooks/isMobile"

interface ResolverState {
  dice_rolls: number[]
  land_casualty_order: string[][]
  naval_casualty_order: string[][]
  mortality_chits: string[][]
  veteran_order: string[]
}

interface Props {
  gameId: number
  zIndex?: number
  onFocus?: () => void
}

export interface DebugPanelHandle {
  open: () => void
}

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_ORIGIN
const PANEL_WIDTH = 448 // px — matches w-[28rem]

const parseStrings = (raw: string): string[] =>
  raw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)

const VALID_CHIT_CODES = new Set(
  Array.from({ length: 30 }, (_, i) => String(i + 1)),
)

const ARABIC_TO_ROMAN: Record<number, string> = {
  1: "I",
  2: "II",
  3: "III",
  4: "IV",
  5: "V",
  6: "VI",
  7: "VII",
  8: "VIII",
  9: "IX",
  10: "X",
  11: "XI",
  12: "XII",
  13: "XIII",
  14: "XIV",
  15: "XV",
  16: "XVI",
  17: "XVII",
  18: "XVIII",
  19: "XIX",
  20: "XX",
  21: "XXI",
  22: "XXII",
  23: "XXIII",
  24: "XXIV",
  25: "XXV",
}

const VALID_ROMAN = new Set(Object.values(ARABIC_TO_ROMAN))

const toRoman = (s: string): string => {
  const n = parseInt(s, 10)
  return ARABIC_TO_ROMAN[n] ?? s.toUpperCase()
}

const validateCasualties = (values: string[]): string | null => {
  if (values.length === 0) return "Enter at least one unit"
  const invalid = values.filter((v) => !VALID_ROMAN.has(v))
  if (invalid.length > 0)
    return `Invalid unit names: ${invalid.join(", ")} — use Roman numerals or numbers 1–25`
  return null
}

const validateChits = (values: string[]): string | null => {
  if (values.length === 0) return "Enter at least one chit"
  const invalid = values.filter((v) => !VALID_CHIT_CODES.has(v))
  if (invalid.length > 0)
    return `Invalid chit codes: ${invalid.join(", ")} — use senator codes 1–30`
  return null
}

const EMPTY_STATE: ResolverState = {
  dice_rolls: [],
  land_casualty_order: [],
  naval_casualty_order: [],
  mortality_chits: [],
  veteran_order: [],
}

type ListQueueSection = {
  label: string
  field: "land_casualty_order" | "naval_casualty_order" | "mortality_chits"
  endpoint: string
  placeholder: string
  parse: (raw: string) => string[]
  validate: (values: string[]) => string | null
  format: (entry: string[]) => string
}

const SECTIONS: ListQueueSection[] = [
  {
    label: "Land casualties",
    field: "land_casualty_order",
    endpoint: "land-casualties",
    placeholder: "e.g. I, III, V",
    parse: (raw) => parseStrings(raw).map(toRoman),
    validate: (v) => validateCasualties(v as string[]),
    format: (entry) => (entry as string[]).join(", "),
  },
  {
    label: "Naval casualties",
    field: "naval_casualty_order",
    endpoint: "naval-casualties",
    placeholder: "e.g. II, IV",
    parse: (raw) => parseStrings(raw).map(toRoman),
    validate: (v) => validateCasualties(v as string[]),
    format: (entry) => (entry as string[]).join(", "),
  },
  {
    label: "Mortality chits",
    field: "mortality_chits",
    endpoint: "chits",
    placeholder: "e.g. 1, 7",
    parse: parseStrings,
    validate: (v) => validateChits(v as string[]),
    format: (entry) => (entry as string[]).join(", "),
  },
]

const DebugPanel = forwardRef<DebugPanelHandle, Props>(function DebugPanel(
  { gameId, zIndex = 1000, onFocus },
  ref,
) {
  const isMobile = useIsMobile()
  const dialogRef = useRef<HTMLDialogElement>(null)

  const [isOpen, setIsOpen] = useState(false)
  const [position, setPosition] = useState({ x: 0, y: 10 })
  const [dragging, setDragging] = useState(false)
  const offsetRef = useRef({ x: 0, y: 0 })

  const [resolverState, setResolverState] = useState<ResolverState>(EMPTY_STATE)
  const [inputs, setInputs] = useState({
    dice_rolls: "",
    land_casualty_order: "",
    naval_casualty_order: "",
    mortality_chits: "",
    veteran_order: "",
  })
  const [enqueueing, setEnqueueing] = useState<keyof ResolverState | null>(null)
  const [errors, setErrors] = useState<
    Partial<Record<keyof ResolverState, string>>
  >({})

  const wsUrl = `${process.env.NEXT_PUBLIC_BACKEND_WS_ORIGIN}/ws/games/${gameId}/debug/`
  const { lastMessage } = useWebSocket(wsUrl, { shouldReconnect: () => true })

  useEffect(() => {
    if (!lastMessage) return
    const data = JSON.parse(lastMessage.data)
    if (data.resolver) setResolverState(data.resolver)
  }, [lastMessage])

  // Centre horizontally on first render
  useEffect(() => {
    setPosition({ x: (window.innerWidth - PANEL_WIDTH) / 2, y: 10 })
  }, [])

  const handleOpen = () => {
    if (isOpen) {
      setPosition({
        x: (window.innerWidth - PANEL_WIDTH) / 2,
        y: 20,
      })
    }
    setIsOpen(true)
    if (isMobile) dialogRef.current?.showModal()
  }

  const handleClose = () => {
    setIsOpen(false)
    if (isMobile) dialogRef.current?.close()
  }

  useImperativeHandle(ref, () => ({ open: handleOpen }))

  const handleMouseDown = (e: React.MouseEvent) => {
    setDragging(true)
    offsetRef.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    }
  }

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (dragging) {
        setPosition({
          x: e.clientX - offsetRef.current.x,
          y: e.clientY - offsetRef.current.y,
        })
      }
    },
    [dragging],
  )

  const handleMouseUp = useCallback(() => setDragging(false), [])

  useEffect(() => {
    if (dragging) {
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
    } else {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [dragging, handleMouseMove, handleMouseUp])

  const handleEnqueueDice = async () => {
    const value = parseInt(inputs.dice_rolls.trim(), 10)
    if (isNaN(value) || value < 1) {
      setErrors((prev) => ({ ...prev, dice_rolls: "Enter a positive integer" }))
      return
    }
    setErrors((prev) => ({ ...prev, dice_rolls: undefined }))
    setEnqueueing("dice_rolls")
    const res = await fetch(`${BACKEND}/api/test/resolver/${gameId}/dice/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ values: [value] }),
    })
    if (res.ok) {
      const data = await res.json()
      setResolverState(data)
      setInputs((prev) => ({ ...prev, dice_rolls: "" }))
    }
    setEnqueueing(null)
  }

  const handleRemoveDice = async (index: number) => {
    const res = await fetch(
      `${BACKEND}/api/test/resolver/${gameId}/dice/${index}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: { "X-CSRFToken": getCSRFToken() },
      },
    )
    if (res.ok) {
      const data = await res.json()
      setResolverState(data)
    }
  }

  const handleEnqueueVeteran = async () => {
    const value = inputs.veteran_order.trim().toUpperCase()
    if (!VALID_ROMAN.has(value)) {
      setErrors((prev) => ({ ...prev, veteran_order: "Enter a Roman numeral I–XXV" }))
      return
    }
    setErrors((prev) => ({ ...prev, veteran_order: undefined }))
    setEnqueueing("veteran_order")
    const res = await fetch(`${BACKEND}/api/test/resolver/${gameId}/veteran/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ values: [value] }),
    })
    if (res.ok) {
      const data = await res.json()
      setResolverState(data)
      setInputs((prev) => ({ ...prev, veteran_order: "" }))
    }
    setEnqueueing(null)
  }

  const handleRemoveVeteran = async (index: number) => {
    const res = await fetch(
      `${BACKEND}/api/test/resolver/${gameId}/veteran/${index}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: { "X-CSRFToken": getCSRFToken() },
      },
    )
    if (res.ok) {
      const data = await res.json()
      setResolverState(data)
    }
  }

  const handleEnqueue = async (section: ListQueueSection) => {
    const values = section.parse(inputs[section.field])
    const error = section.validate(values)
    if (error) {
      setErrors((prev) => ({ ...prev, [section.field]: error }))
      return
    }
    setErrors((prev) => ({ ...prev, [section.field]: undefined }))
    setEnqueueing(section.field)
    const res = await fetch(
      `${BACKEND}/api/test/resolver/${gameId}/${section.endpoint}/`,
      {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({ values }),
      },
    )
    if (res.ok) {
      const data = await res.json()
      setResolverState(data)
      setInputs((prev) => ({ ...prev, [section.field]: "" }))
    }
    setEnqueueing(null)
  }

  const handleRemove = async (section: ListQueueSection, index: number) => {
    const res = await fetch(
      `${BACKEND}/api/test/resolver/${gameId}/${section.endpoint}/${index}/`,
      {
        method: "DELETE",
        credentials: "include",
        headers: { "X-CSRFToken": getCSRFToken() },
      },
    )
    if (res.ok) {
      const data = await res.json()
      setResolverState(data)
    }
  }

  const handleClearAll = async () => {
    const res = await fetch(`${BACKEND}/api/test/resolver/${gameId}/`, {
      method: "DELETE",
      credentials: "include",
      headers: { "X-CSRFToken": getCSRFToken() },
    })
    if (res.ok) setResolverState(EMPTY_STATE)
  }

  const totalPending =
    resolverState.dice_rolls.length +
    resolverState.veteran_order.length +
    SECTIONS.reduce(
      (sum, s) => sum + (resolverState[s.field] as string[][]).length,
      0,
    )

  const content = (
    <>
      <div
        className={`flex items-center justify-between px-6 py-4 ${isMobile ? "" : "cursor-grab select-none"}`}
        onMouseDown={isMobile ? undefined : handleMouseDown}
      >
        <h2 className="text-xl">Debug Tools</h2>
        <button
          onClick={handleClose}
          className="text-neutral-600 hover:text-black"
        >
          ✕
        </button>
      </div>

      <div className="flex flex-col gap-5 px-6 pb-6">
        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between">
            <span className="font-semibold">Random Resolver</span>
            {totalPending > 0 && (
              <button
                onClick={handleClearAll}
                className="text-sm text-red-600 hover:underline"
              >
                Clear all
              </button>
            )}
          </div>
          <p className="text-sm text-neutral-500">
            Override the otherwise random outcomes of dice rolls, casualties,
            and mortality chits for upcoming game actions. Queued items are
            stored in the server cache and will be cleared on restart.
          </p>
        </div>

        {/* Dice rolls — one entry per roll_dice() call */}
        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium">
            Dice rolls
            {resolverState.dice_rolls.length > 0 && (
              <span className="ml-1 text-sm font-normal text-neutral-500">
                ({resolverState.dice_rolls.length} queued)
              </span>
            )}
          </span>
          {resolverState.dice_rolls.length > 0 && (
            <ol className="flex flex-col gap-1">
              {resolverState.dice_rolls.map((value, i) => (
                <li
                  key={i}
                  className="flex items-center justify-between gap-2 rounded bg-neutral-50 px-2 py-1 text-sm"
                >
                  <span className="min-w-0 flex-1">
                    <span className="mr-1 font-mono text-sm text-neutral-400">
                      {i + 1}.
                    </span>
                    <span className="text-neutral-700">{value}</span>
                  </span>
                  <button
                    onClick={() => handleRemoveDice(i)}
                    className="shrink-0 text-sm text-neutral-400 hover:text-red-600"
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ol>
          )}
          <div className="flex flex-col gap-1">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputs.dice_rolls}
                onChange={(e) => {
                  setInputs((prev) => ({ ...prev, dice_rolls: e.target.value }))
                  setErrors((prev) => ({ ...prev, dice_rolls: undefined }))
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleEnqueueDice()
                }}
                placeholder="e.g. 18"
                className={`min-w-0 flex-1 rounded border px-2 py-1 text-sm ${errors.dice_rolls ? "border-red-400" : "border-neutral-300"}`}
              />
              <button
                onClick={handleEnqueueDice}
                disabled={enqueueing === "dice_rolls" || !inputs.dice_rolls.trim()}
                className="select-none rounded-md border border-blue-600 bg-white px-3 py-1 text-sm text-blue-600 hover:bg-blue-100 disabled:cursor-not-allowed disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-white"
              >
                {enqueueing === "dice_rolls" ? "…" : "Add"}
              </button>
            </div>
            {errors.dice_rolls && (
              <p className="text-sm text-red-600">{errors.dice_rolls}</p>
            )}
          </div>
        </div>

        {SECTIONS.map((section) => {
          const queue = resolverState[section.field] as string[][]
          const isEnqueueing = enqueueing === section.field
          return (
            <div key={section.field} className="flex flex-col gap-2">
              <span className="text-sm font-medium">
                {section.label}
                {queue.length > 0 && (
                  <span className="ml-1 text-sm font-normal text-neutral-500">
                    ({queue.length} queued)
                  </span>
                )}
              </span>

              {queue.length > 0 && (
                <ol className="flex flex-col gap-1">
                  {queue.map((entry, i) => (
                    <li
                      key={i}
                      className="flex items-center justify-between gap-2 rounded bg-neutral-50 px-2 py-1 text-sm"
                    >
                      <span className="min-w-0 flex-1">
                        <span className="mr-1 font-mono text-sm text-neutral-400">
                          {i + 1}.
                        </span>
                        <span className="text-neutral-700">
                          {section.format(entry as string[])}
                        </span>
                      </span>
                      <button
                        onClick={() => handleRemove(section, i)}
                        className="shrink-0 text-sm text-neutral-400 hover:text-red-600"
                      >
                        ✕
                      </button>
                    </li>
                  ))}
                </ol>
              )}

              <div className="flex flex-col gap-1">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={inputs[section.field]}
                    onChange={(e) => {
                      setInputs((prev) => ({
                        ...prev,
                        [section.field]: e.target.value,
                      }))
                      setErrors((prev) => ({
                        ...prev,
                        [section.field]: undefined,
                      }))
                    }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleEnqueue(section)
                    }}
                    placeholder={section.placeholder}
                    className={`min-w-0 flex-1 rounded border px-2 py-1 text-sm ${errors[section.field] ? "border-red-400" : "border-neutral-300"}`}
                  />
                  <button
                    onClick={() => handleEnqueue(section)}
                    disabled={isEnqueueing || !inputs[section.field].trim()}
                    className="select-none rounded-md border border-blue-600 bg-white px-3 py-1 text-sm text-blue-600 hover:bg-blue-100 disabled:cursor-not-allowed disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-white"
                  >
                    {isEnqueueing ? "…" : "Add"}
                  </button>
                </div>
                {errors[section.field] && (
                  <p className="text-sm text-red-600">
                    {errors[section.field]}
                  </p>
                )}
              </div>
            </div>
          )
        })}

        {/* Veteran selection — one entry per select_veteran() call */}
        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium">
            Veteran selection
            {resolverState.veteran_order.length > 0 && (
              <span className="ml-1 text-sm font-normal text-neutral-500">
                ({resolverState.veteran_order.length} queued)
              </span>
            )}
          </span>
          {resolverState.veteran_order.length > 0 && (
            <ol className="flex flex-col gap-1">
              {resolverState.veteran_order.map((value, i) => (
                <li
                  key={i}
                  className="flex items-center justify-between gap-2 rounded bg-neutral-50 px-2 py-1 text-sm"
                >
                  <span className="min-w-0 flex-1">
                    <span className="mr-1 font-mono text-sm text-neutral-400">
                      {i + 1}.
                    </span>
                    <span className="text-neutral-700">{value}</span>
                  </span>
                  <button
                    onClick={() => handleRemoveVeteran(i)}
                    className="shrink-0 text-sm text-neutral-400 hover:text-red-600"
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ol>
          )}
          <div className="flex flex-col gap-1">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputs.veteran_order}
                onChange={(e) => {
                  setInputs((prev) => ({ ...prev, veteran_order: e.target.value }))
                  setErrors((prev) => ({ ...prev, veteran_order: undefined }))
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleEnqueueVeteran()
                }}
                placeholder="e.g. III"
                className={`min-w-0 flex-1 rounded border px-2 py-1 text-sm ${errors.veteran_order ? "border-red-400" : "border-neutral-300"}`}
              />
              <button
                onClick={handleEnqueueVeteran}
                disabled={enqueueing === "veteran_order" || !inputs.veteran_order.trim()}
                className="select-none rounded-md border border-blue-600 bg-white px-3 py-1 text-sm text-blue-600 hover:bg-blue-100 disabled:cursor-not-allowed disabled:border-neutral-300 disabled:text-neutral-400 disabled:hover:bg-white"
              >
                {enqueueing === "veteran_order" ? "…" : "Add"}
              </button>
            </div>
            {errors.veteran_order && (
              <p className="text-sm text-red-600">{errors.veteran_order}</p>
            )}
          </div>
        </div>
      </div>
    </>
  )

  return (
    <>
      {isMobile ? (
        <dialog
          ref={dialogRef}
          className="w-[90vw] max-w-[448px] rounded-md border shadow-lg"
        >
          {content}
        </dialog>
      ) : (
        <div
          className="rounded-lg border border-neutral-400 bg-white shadow-lg"
          style={{
            position: "fixed",
            top: position.y,
            left: position.x,
            zIndex,
            cursor: dragging ? "grabbing" : "default",
            width: `${PANEL_WIDTH}px`,
            display: isOpen ? "block" : "none",
          }}
          onMouseDown={onFocus}
        >
          {content}
        </div>
      )}
    </>
  )
})

export default DebugPanel
