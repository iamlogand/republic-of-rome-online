"use client"

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react"

import PublicGameState from "@/classes/PublicGameState"
import {
  PersuasionSnapshot,
  createPersuasionSnapshot,
} from "@/helpers/persuasion"

import PersuasionCalculationPanel, {
  PersuasionCalculationState,
} from "./PersuasionCalculationPanel"

interface Props {
  publicGameState: PublicGameState
  factionId: number
  zIndex?: number
  onFocus?: () => void
}

export interface PersuasionCalculatorHandle {
  open: () => void
}

const newCalculation = (id: number): PersuasionCalculationState => ({
  id,
  persuaderId: null,
  targetId: null,
  persuaderBribe: 0,
  counterBribes: {},
  useSeduction: false,
  useBlackmail: false,
})

const PersuasionCalculator = forwardRef<PersuasionCalculatorHandle, Props>(
  function PersuasionCalculator(
    { publicGameState, factionId, zIndex = 1000, onFocus }: Props,
    ref,
  ) {
    const [isOpen, setIsOpen] = useState(false)
    const [snapshot, setSnapshot] = useState<PersuasionSnapshot | null>(null)
    const [position, setPosition] = useState({ x: 80, y: 20 })
    const [dragging, setDragging] = useState(false)
    const offsetRef = useRef({ x: 0, y: 0 })
    const nextIdRef = useRef(2)
    const [calculations, setCalculations] = useState<
      PersuasionCalculationState[]
    >([newCalculation(1)])
    const [selectedId, setSelectedId] = useState(1)

    const close = useCallback(() => {
      setIsOpen(false)
    }, [])

    useImperativeHandle(
      ref,
      () => ({
        open: () => {
          if (isOpen) {
            onFocus?.()
            setPosition({
              x: Math.max(10, (window.innerWidth - 760) / 2),
              y: 20,
            })
            return
          }
          setSnapshot(createPersuasionSnapshot(publicGameState, factionId))
          setCalculations([newCalculation(1)])
          setSelectedId(1)
          nextIdRef.current = 2
          setIsOpen(true)
          onFocus?.()
          setPosition((current) => ({
            x: Math.max(10, (window.innerWidth - 760) / 2),
            y: current.y,
          }))
        },
      }),
      [factionId, isOpen, onFocus, publicGameState],
    )

    const handleMouseDown = (event: React.MouseEvent) => {
      setDragging(true)
      offsetRef.current = {
        x: event.clientX - position.x,
        y: event.clientY - position.y,
      }
    }

    const handleMouseMove = useCallback(
      (event: MouseEvent) => {
        if (!dragging) return
        setPosition({
          x: event.clientX - offsetRef.current.x,
          y: event.clientY - offsetRef.current.y,
        })
      },
      [dragging],
    )

    const handleMouseUp = useCallback(() => setDragging(false), [])

    useEffect(() => {
      if (!dragging) return
      document.addEventListener("mousemove", handleMouseMove)
      document.addEventListener("mouseup", handleMouseUp)
      return () => {
        document.removeEventListener("mousemove", handleMouseMove)
        document.removeEventListener("mouseup", handleMouseUp)
      }
    }, [dragging, handleMouseMove, handleMouseUp])

    const selectedCalculation =
      calculations.find((calculation) => calculation.id === selectedId) ??
      calculations[0]

    const updateSelected = (
      update: Partial<Omit<PersuasionCalculationState, "id">>,
    ) => {
      setCalculations((current) =>
        current.map((calculation) =>
          calculation.id === selectedId
            ? { ...calculation, ...update }
            : calculation,
        ),
      )
    }

    const addCalculation = () => {
      const id = nextIdRef.current++
      setCalculations((current) => [...current, newCalculation(id)])
      setSelectedId(id)
    }

    const removeCalculation = (id: number) => {
      if (calculations.length === 1) return
      const remaining = calculations.filter(
        (calculation) => calculation.id !== id,
      )
      setCalculations(remaining)
      if (selectedId === id) setSelectedId(remaining[0].id)
    }

    const focusTab = (id: number) => {
      setSelectedId(id)
      requestAnimationFrame(() =>
        document.getElementById(`persuasion-tab-${id}`)?.focus(),
      )
    }

    const handleTabKeyDown = (
      event: React.KeyboardEvent<HTMLButtonElement>,
      index: number,
    ) => {
      let nextIndex: number | null = null
      if (event.key === "ArrowRight") {
        nextIndex = (index + 1) % calculations.length
      } else if (event.key === "ArrowLeft") {
        nextIndex = (index - 1 + calculations.length) % calculations.length
      } else if (event.key === "Home") {
        nextIndex = 0
      } else if (event.key === "End") {
        nextIndex = calculations.length - 1
      }
      if (nextIndex === null) return
      event.preventDefault()
      focusTab(calculations[nextIndex].id)
    }

    if (!isOpen || !snapshot || !selectedCalculation) return null

    const selectedTabId = `persuasion-tab-${selectedCalculation.id}`
    const selectedPanelId = `persuasion-panel-${selectedCalculation.id}`

    return (
      <section
        aria-labelledby="persuasion-calculator-title"
        className="fixed w-[760px] rounded-lg border border-neutral-400 bg-white shadow-lg"
        style={{ left: position.x, top: position.y, zIndex }}
        onMouseDown={onFocus}
        onFocusCapture={onFocus}
      >
        <header
          className="flex cursor-grab select-none items-center justify-between px-6 py-5"
          onMouseDown={handleMouseDown}
        >
          <h2 id="persuasion-calculator-title" className="text-xl">
            Persuasion Calculator
          </h2>
          <button
            type="button"
            aria-label="Close persuasion calculator"
            onMouseDown={(event) => event.stopPropagation()}
            onClick={close}
            className="text-neutral-600 hover:text-black"
          >
            ✕
          </button>
        </header>

        <div className="px-6 pb-6">
          <div className="mb-4 flex flex-col gap-1 text-sm text-neutral-600">
            <p>
              Private virtual planning tool. These values stay in your browser
              and cannot affect the game.
            </p>
            <p>
              This snapshot was taken when the calculator opened. Close and
              reopen it to use the latest game state.
            </p>
            <p>
              All entered talents are hypothetical additions to the captured
              values.
            </p>
          </div>

          <div
            role="tablist"
            aria-label="Persuasion calculations"
            className="mx-[-24px] mb-5 flex flex-wrap items-center gap-2 bg-neutral-100 px-6 py-2"
          >
            {calculations.map((calculation, index) => {
              const calculationTarget = snapshot.targets.find(
                (senator) => senator.id === calculation.targetId,
              )
              const selected = calculation.id === selectedId
              const tabId = `persuasion-tab-${calculation.id}`
              const panelId = `persuasion-panel-${calculation.id}`
              return (
                <div
                  key={calculation.id}
                  className={`flex items-center rounded-md ${
                    selected
                      ? "border border-neutral-400 bg-white"
                      : "p-px text-neutral-600 hover:bg-white"
                  }`}
                >
                  <button
                    id={tabId}
                    type="button"
                    role="tab"
                    aria-selected={selected}
                    aria-controls={panelId}
                    tabIndex={selected ? 0 : -1}
                    onClick={() => setSelectedId(calculation.id)}
                    onKeyDown={(event) => handleTabKeyDown(event, index)}
                    className="px-2 py-1"
                  >
                    {calculationTarget?.displayName ??
                      `Calculation ${index + 1}`}
                  </button>
                  {calculations.length > 1 && (
                    <button
                      type="button"
                      aria-label={`Remove calculation ${index + 1}`}
                      onClick={() => removeCalculation(calculation.id)}
                      className="mr-1.5 flex h-5 w-5 items-center justify-center rounded-full text-xs text-neutral-600 hover:bg-neutral-200"
                    >
                      ✕
                    </button>
                  )}
                </div>
              )
            })}
            <button
              type="button"
              aria-label="Add persuasion calculation"
              onClick={addCalculation}
              className="flex h-8 w-8 items-center justify-center rounded-full text-2xl hover:bg-neutral-200"
            >
              +
            </button>
          </div>

          <div
            id={selectedPanelId}
            role="tabpanel"
            aria-labelledby={selectedTabId}
          >
            <PersuasionCalculationPanel
              calculation={selectedCalculation}
              snapshot={snapshot}
              updateCalculation={updateSelected}
            />
          </div>

          <div className="mt-6 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
            <strong>Prototype limitation:</strong> Statesman loyalty modifiers,
            including the Gracchi exception, are not included. The target&apos;s
            snapshot Loyalty value is used unchanged.
          </div>

          <div className="mt-5 flex justify-end">
            <button
              type="button"
              onClick={close}
              className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
            >
              Close
            </button>
          </div>
        </div>
      </section>
    )
  },
)

export default PersuasionCalculator
