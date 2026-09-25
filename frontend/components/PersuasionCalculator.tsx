"use client"

import { useEffect, useRef, useState } from "react"
import React from "react"

import PublicGameState from "@/classes/PublicGameState"
import { getEvilOmensLevel } from "@/helpers/gameEffects"

import PersuasionCalculationPanel, {
  PersuasionCalculationState,
} from "./PersuasionCalculationPanel"

interface Props {
  publicGameState: PublicGameState
  isOpen: boolean
  onClose: () => void
  zIndex?: number
  onFocus?: () => void
}

const newCalculation = (
  id: number,
  evilOmens = 0,
  eraEnds = false,
): PersuasionCalculationState => ({
  id,
  persuaderId: null,
  targetId: null,
  persuaderBribe: 0,
  counterBribes: 0,
  evilOmens,
  eraEnds,
})

const PersuasionCalculator = ({
  publicGameState,
  isOpen,
  onClose,
  zIndex = 1000,
  onFocus,
}: Props) => {
  const [position, setPosition] = useState({ x: 80, y: 20 })
  const [dragging, setDragging] = useState(false)
  const offsetRef = useRef({ x: 0, y: 0 })
  const nextIdRef = useRef(2)
  const initializedRef = useRef(false)
  const [calculations, setCalculations] = useState<
    PersuasionCalculationState[]
  >([newCalculation(1)])
  const [selectedId, setSelectedId] = useState(1)

  useEffect(() => {
    if (!isOpen || initializedRef.current) return
    initializedRef.current = true
    setCalculations([
      newCalculation(
        1,
        getEvilOmensLevel(publicGameState.game?.effects ?? []),
        publicGameState.game?.eraEnds ?? false,
      ),
    ])
    setSelectedId(1)
    nextIdRef.current = 2
    setPosition((current) => ({
      x: Math.max(10, (window.innerWidth - 760) / 2),
      y: current.y,
    }))
  }, [isOpen, publicGameState])

  useEffect(() => {
    if (!dragging) return
    const handleMouseMove = (event: MouseEvent) => {
      setPosition({
        x: event.clientX - offsetRef.current.x,
        y: event.clientY - offsetRef.current.y,
      })
    }
    const handleMouseUp = () => setDragging(false)
    document.addEventListener("mousemove", handleMouseMove)
    document.addEventListener("mouseup", handleMouseUp)
    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [dragging])

  const selectedCalculation =
    calculations.find((c) => c.id === selectedId) ?? calculations[0]

  const updateSelected = (
    update: Partial<Omit<PersuasionCalculationState, "id">>,
  ) => {
    setCalculations((current) =>
      current.map((c) => (c.id === selectedId ? { ...c, ...update } : c)),
    )
  }

  const addCalculation = () => {
    const id = nextIdRef.current++
    setCalculations((current) => [
      ...current,
      newCalculation(
        id,
        getEvilOmensLevel(publicGameState.game?.effects ?? []),
        publicGameState.game?.eraEnds ?? false,
      ),
    ])
    setSelectedId(id)
  }

  const removeCalculation = (id: number) => {
    if (calculations.length === 1) return
    const remaining = calculations.filter((c) => c.id !== id)
    setCalculations(remaining)
    if (selectedId === id) setSelectedId(remaining[0].id)
  }

  const handleTabKeyDown = (
    event: React.KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) => {
    let nextIndex: number | null = null
    if (event.key === "ArrowRight")
      nextIndex = (index + 1) % calculations.length
    else if (event.key === "ArrowLeft")
      nextIndex = (index - 1 + calculations.length) % calculations.length
    else if (event.key === "Home") nextIndex = 0
    else if (event.key === "End") nextIndex = calculations.length - 1
    if (nextIndex === null) return
    event.preventDefault()
    const nextTabId = calculations[nextIndex].id
    setSelectedId(nextTabId)
    requestAnimationFrame(() =>
      document.getElementById(`persuasion-tab-${nextTabId}`)?.focus(),
    )
  }

  if (!isOpen || !selectedCalculation) return null

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
        className="flex cursor-grab select-none items-center justify-between px-6 py-6"
        onMouseDown={(event) => {
          setDragging(true)
          offsetRef.current = {
            x: event.clientX - position.x,
            y: event.clientY - position.y,
          }
        }}
      >
        <h2 id="persuasion-calculator-title" className="text-xl">
          Persuasion Calculator
        </h2>
        <button
          type="button"
          aria-label="Close persuasion calculator"
          onMouseDown={(event) => event.stopPropagation()}
          onClick={onClose}
          className="text-neutral-600 hover:text-black"
        >
          ✕
        </button>
      </header>

      <div className="px-6 pb-6">
        <div
          role="tablist"
          aria-label="Persuasion calculations"
          className="mx-[-24px] flex flex-wrap items-center gap-2 bg-neutral-100 px-6 py-2"
        >
          {calculations.map((calculation, index) => {
            const calculationTarget = publicGameState.senators.find(
              (s) => s.id === calculation.targetId,
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
                  {calculationTarget?.displayName ?? `Calculation ${index + 1}`}
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
          className="pt-6"
        >
          <PersuasionCalculationPanel
            calculation={selectedCalculation}
            publicGameState={publicGameState}
            updateCalculation={updateSelected}
          />
        </div>

        <div className="mt-4 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
          >
            Close
          </button>
        </div>
      </div>
    </section>
  )
}

export default PersuasionCalculator
