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
  showPlayerButtons: boolean
  onShowPlayerButtonsChange: (show: boolean) => void
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

const VALID_UNIT_NUMBERS = new Set(
  Array.from({ length: 25 }, (_, i) => String(i + 1)),
)

const validateUnitNumbers = (values: string[]): string | null => {
  if (values.length === 0) return "Enter at least one unit"
  const invalid = values.filter((v) => !VALID_UNIT_NUMBERS.has(v))
  if (invalid.length > 0)
    return `Invalid unit numbers: ${invalid.join(", ")} — use 1–25`
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

type QueueSection = {
  label: string
  field: keyof ResolverState
  endpoint: string
  placeholder: string
  parse: (raw: string) => unknown[]
  validate: (values: unknown[]) => string | null
  format: (entry: unknown) => string
}

const SECTIONS: QueueSection[] = [
  {
    label: "Dice rolls",
    field: "dice_rolls",
    endpoint: "dice",
    placeholder: "e.g. 18",
    parse: (raw) => [parseInt(raw.trim(), 10)],
    validate: ([value]) => {
      const n = value as number
      if (isNaN(n) || n < 1) return "Enter a positive integer"
      return null
    },
    format: (entry) => String(entry),
  },
  {
    label: "Land casualties",
    field: "land_casualty_order",
    endpoint: "land-casualties",
    placeholder: "e.g. 1, 3, 5",
    parse: parseStrings,
    validate: (values) => validateUnitNumbers(values as string[]),
    format: (entry) => (entry as string[]).join(", "),
  },
  {
    label: "Naval casualties",
    field: "naval_casualty_order",
    endpoint: "naval-casualties",
    placeholder: "e.g. 2, 4",
    parse: parseStrings,
    validate: (values) => validateUnitNumbers(values as string[]),
    format: (entry) => (entry as string[]).join(", "),
  },
  {
    label: "Mortality chits",
    field: "mortality_chits",
    endpoint: "chits",
    placeholder: "e.g. 1, 7",
    parse: parseStrings,
    validate: (values) => validateChits(values as string[]),
    format: (entry) => (entry as string[]).join(", "),
  },
  {
    label: "Veteran selection",
    field: "veteran_order",
    endpoint: "veteran",
    placeholder: "e.g. 5",
    parse: (raw) => [raw.trim()],
    validate: ([value]) => {
      if (!VALID_UNIT_NUMBERS.has(value as string)) return "Enter a number 1–25"
      return null
    },
    format: (entry) => entry as string,
  },
]

const DebugPanel = forwardRef<DebugPanelHandle, Props>(function DebugPanel(
  {
    gameId,
    zIndex = 1000,
    onFocus,
    showPlayerButtons,
    onShowPlayerButtonsChange,
  },
  ref,
) {
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
  }

  const handleClose = () => setIsOpen(false)

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

  const handleEnqueue = async (section: QueueSection) => {
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

  const handleRemove = async (section: QueueSection, index: number) => {
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

  const totalPending = SECTIONS.reduce(
    (sum, s) => sum + (resolverState[s.field] as unknown[]).length,
    0,
  )

  const content = (
    <>
      <div
        className="flex cursor-grab select-none items-center justify-between px-6 py-4"
        onMouseDown={handleMouseDown}
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
            <span className="font-semibold">Player Buttons</span>
            <button
              onClick={() => onShowPlayerButtonsChange(!showPlayerButtons)}
              className="rounded border border-blue-600 px-2 text-sm text-blue-600 hover:bg-blue-100"
            >
              {showPlayerButtons ? "Hide" : "Show"}
            </button>
          </div>
          <p className="text-sm text-neutral-500">
            Add a button per player to the game bar, so one window can be played
            as every faction. Switching signs this browser in as that player and
            reloads.
          </p>
        </div>

        <hr className="border-neutral-300" />

        <div className="flex flex-col gap-1">
          <div className="flex items-center justify-between">
            <span className="font-semibold">Fake Random Resolver</span>
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

        {SECTIONS.map((section) => {
          const queue = resolverState[section.field] as unknown[]
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
                          {section.format(entry)}
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
      </div>
    </>
  )

  return (
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
  )
})

export default DebugPanel
