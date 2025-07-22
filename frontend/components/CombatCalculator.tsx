import { useCallback, useEffect, useRef, useState } from "react"
import React from "react"

import CombatCalculation from "@/classes/CombatCalculation"
import PublicGameState from "@/classes/PublicGameState"
import useIsMobile from "@/hooks/isMobile"

import CombatCalculatorItem from "./CombatCalculatorItem"

interface ActionHandlerProps {
  publicGameState: PublicGameState
  combatCalculations: CombatCalculation[]
  updateCombatCalculations: (combatCalculations: CombatCalculation[]) => void
}

const CombatCalculator = ({
  publicGameState,
  combatCalculations,
  updateCombatCalculations,
}: ActionHandlerProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const [position, setPosition] = useState({
    x: (window.innerWidth - 800) / 2,
    y: 10,
  })
  const [dragging, setDragging] = useState(false)
  const offsetRef = useRef({ x: 0, y: 0 })
  const hasNewTabRef = useRef(false)

  const dialogRef = useRef<HTMLDialogElement>(null)
  const isMobile = useIsMobile()

  const [selectedCalculationId, setSelectedCalculationId] = useState<
    number | null
  >(combatCalculations[0]?.id || null)

  const handleOpen = () => {
    if (isOpen) {
      setPosition({
        x: (window.innerWidth - 800) / 2,
        y: 20,
      })
    }
    setIsOpen(true)
    if (isMobile) {
      dialogRef.current?.showModal()
    }
  }

  const handleClose = () => {
    setIsOpen(false)
    if (isMobile) {
      dialogRef.current?.close()
    }
  }

  useEffect(() => {
    setPosition((pos) => ({
      x: (window.innerWidth - 800) / 2,
      y: pos.y,
    }))
  }, [])

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

  const handleMouseUp = useCallback(() => {
    setDragging(false)
  }, [])

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

  const addTab = () => {
    if (!publicGameState.game) return
    const newCalculation = new CombatCalculation({
      id: null,
      game: publicGameState.game.id,
      name: "Combat",
      commander: null,
      war: null,
      land_battle: true,
      legions: 0,
      veteran_legions: 0,
      fleets: 0,
    })

    const updatedCalculations = [...combatCalculations, newCalculation]
    updateCombatCalculations(updatedCalculations)
    hasNewTabRef.current = true
  }

  const removeTab = (id: number | null) => {
    if (id !== null && combatCalculations.length > 1) {
      const filteredCalculations = combatCalculations.filter(
        (calculation) => calculation.id !== id,
      )
      updateCombatCalculations(filteredCalculations)

      if (selectedCalculationId === id && filteredCalculations.length > 0) {
        setSelectedCalculationId(filteredCalculations[0].id)
      }
    }
  }

  // Select the last tab if it's the newest one
  useEffect(() => {
    if (
      hasNewTabRef.current &&
      !combatCalculations.some((c) => c.id === null)
    ) {
      const lastCalculation = combatCalculations[combatCalculations.length - 1]
      setSelectedCalculationId(lastCalculation.id)
      hasNewTabRef.current = false
    }
  }, [combatCalculations])

  const updateCombatCalculation = (updatedCalculation: CombatCalculation) => {
    updateCombatCalculations(
      combatCalculations.map((c) =>
        c.id === updatedCalculation.id ? updatedCalculation : c,
      ),
    )
  }

  // Shared content to render in both desktop and mobile
  const CalculatorContent = (
    <>
      <div
        className={`flex items-center justify-between px-6 py-6 ${isMobile ? "" : "cursor-grab select-none"}`}
        onMouseDown={isMobile ? () => {} : handleMouseDown}
      >
        <h3 className="text-xl">Combat Calculator</h3>
        <button
          onClick={handleClose}
          className="text-neutral-600 hover:text-black"
        >
          ✕
        </button>
      </div>

      <div className="px-6 pb-6">
        <div className="mx-[-24px] flex max-w-[800px] select-none flex-wrap items-center gap-2 border-neutral-400 bg-neutral-100 px-6 py-2">
          {combatCalculations.map((calculation, index) => {
            const isLast = index === combatCalculations.length - 1
            const tabContent = (
              <div
                key={calculation.id}
                className={`flex flex-row items-center rounded-md ${
                  calculation.id === selectedCalculationId
                    ? "border border-neutral-400 bg-white"
                    : "p-px text-neutral-600 hover:bg-white"
                }`}
              >
                <button
                  className="px-2 py-1"
                  onClick={() => setSelectedCalculationId(calculation.id)}
                  disabled={calculation.id === selectedCalculationId}
                >
                  {calculation.name}
                </button>
                {combatCalculations.length > 1 && (
                  <button
                    className="mr-1.5 flex h-5 w-5 items-center justify-center rounded-full text-xs text-neutral-700 hover:bg-neutral-200"
                    onClick={() => removeTab(calculation.id)}
                  >
                    ✕
                  </button>
                )}
              </div>
            )

            if (isLast) {
              return (
                <div key={calculation.id} className="flex items-center gap-2">
                  {tabContent}
                  <button
                    className="flex h-8 w-8 items-center justify-center rounded-full text-2xl hover:bg-neutral-200"
                    onClick={addTab}
                    disabled={combatCalculations.some((c) => c.id === null)}
                  >
                    +
                  </button>
                </div>
              )
            }

            return tabContent
          })}
        </div>

        {combatCalculations
          .sort((a, b) => {
            if (a.id == null && b.id == null) return 0
            if (a.id == null) return 1
            if (b.id == null) return -1
            return a.id - b.id
          })
          .map((calculation) => {
            const shouldDisplay =
              calculation.id === selectedCalculationId ||
              (selectedCalculationId === null && calculation.id === null)

            return (
              <div
                key={calculation.id || "new"}
                style={{
                  display: shouldDisplay ? "block" : "none",
                }}
              >
                <CombatCalculatorItem
                  publicGameState={publicGameState}
                  combatCalculation={calculation}
                  updateCombatCalculation={updateCombatCalculation}
                />
              </div>
            )
          })}

        <div className="mt-4 flex justify-end gap-4">
          <button
            type="button"
            onClick={handleClose}
            className="select-none rounded-md border border-neutral-600 px-4 py-1 text-neutral-600 hover:bg-neutral-100"
          >
            Close
          </button>
        </div>
      </div>
    </>
  )

  return (
    <>
      <button
        type="button"
        onClick={handleOpen}
        className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100"
      >
        Combat Calculator
      </button>

      {isMobile ? (
        <dialog
          ref={dialogRef}
          className="w-[90vw] max-w-[600px] rounded-md border shadow-lg"
        >
          {CalculatorContent}
        </dialog>
      ) : (
        <div
          className="rounded-lg border bg-white shadow-lg"
          style={{
            position: "fixed",
            top: position.y,
            left: position.x,
            zIndex: 1000,
            cursor: dragging ? "grabbing" : "default",
            width: "800px",
            display: isOpen ? "block" : "none",
          }}
        >
          {CalculatorContent}
        </div>
      )}
    </>
  )
}

export default CombatCalculator
