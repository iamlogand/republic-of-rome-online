import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import React from "react"

import { SelectField } from "@/classes/AvailableAction"
import CombatCalculation from "@/classes/CombatCalculation"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import useIsMobile from "@/hooks/isMobile"
import {
  createProposalCalculation,
  getDeployedForces,
} from "@/utils/deploymentProposal"

import CombatCalculatorItem from "./CombatCalculatorItem"

interface ActionHandlerProps {
  publicGameState: PublicGameState
  privateGameState: PrivateGameState | undefined
  combatCalculations: CombatCalculation[]
  updateCombatCalculations: (combatCalculations: CombatCalculation[]) => void
  onTransferToProposal: (calculation: CombatCalculation) => void
}

const CombatCalculator = ({
  publicGameState,
  privateGameState,
  combatCalculations,
  updateCombatCalculations,
  onTransferToProposal,
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
    number | "proposal" | null
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

  const addTab = useCallback(() => {
    if (!publicGameState.game) return
    const newCalculation = new CombatCalculation({
      id: null,
      game: publicGameState.game.id,
      name: "Untitled",
      commander: null,
      war: null,
      land_battle: false,
      regular_legions: 0,
      veteran_legions: 0,
      fleets: 0,
    })

    const updatedCalculations = [...combatCalculations, newCalculation]
    updateCombatCalculations(updatedCalculations)
    hasNewTabRef.current = true
  }, [combatCalculations, publicGameState.game, updateCombatCalculations])

  const removeTab = (id: number | "proposal" | null) => {
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

  // Create proposal calculation if current proposal is a deployment
  const proposalCalculation = useMemo(() => {
    return createProposalCalculation(publicGameState)
  }, [publicGameState])

  // Combine proposal calculation with user calculations
  const allCalculations = useMemo(() => {
    if (proposalCalculation) {
      return [proposalCalculation, ...combatCalculations]
    }
    return combatCalculations
  }, [proposalCalculation, combatCalculations])

  useEffect(() => {
    // If proposal exists and no tab is selected, select it
    if (proposalCalculation && !selectedCalculationId) {
      setSelectedCalculationId("proposal")
      return
    }

    if (combatCalculations.length > 0) {
      if (
        hasNewTabRef.current &&
        !combatCalculations.some((c) => c.id === null)
      ) {
        // If this user just created a new tab, select it
        const lastCalculation =
          combatCalculations[combatCalculations.length - 1]
        setSelectedCalculationId(lastCalculation.id)
        hasNewTabRef.current = false
        return
      }

      // Check if currently selected tab still exists
      const selectedExists =
        selectedCalculationId === "proposal"
          ? !!proposalCalculation
          : combatCalculations.some((c) => c.id === selectedCalculationId)

      if (!selectedExists) {
        // Select first available tab
        const firstTab = proposalCalculation
          ? "proposal"
          : combatCalculations[0]?.id
        if (firstTab) {
          setSelectedCalculationId(firstTab)
        }
      }
    } else {
      // If there are no tabs, make a new one
      addTab()
    }
  }, [combatCalculations, addTab, proposalCalculation, selectedCalculationId])

  const updateCombatCalculation = (updatedCalculation: CombatCalculation) => {
    updateCombatCalculations(
      combatCalculations.map((c) =>
        c.id === updatedCalculation.id ? updatedCalculation : c,
      ),
    )
  }

  // Validation for Transfer to proposal button
  const getTransferStatus = useCallback(
    (calculation: CombatCalculation) => {
      if (!privateGameState) {
        return { canTransfer: false, isVisible: false, reason: "" }
      }

      const deployAction = privateGameState.availableActions.find(
        (action) => action.name === "Propose deploying forces",
      )

      if (!deployAction) {
        return { canTransfer: false, isVisible: false, reason: "" }
      }

      let canTransfer = true
      let reason = ""

      if (calculation.commander === null) {
        canTransfer = false
        reason = "No commander selected"
      } else {
        const commanderField = deployAction.schema.find(
          (field) => field.name === "Commander",
        )
        const commanderAvailable = (
          commanderField as SelectField
        )?.options?.some((option) => option.id === calculation.commander)
        if (!commanderAvailable) {
          canTransfer = false
          reason = "Commander not available for deployment"
        }
      }

      if (canTransfer && calculation.war === null) {
        canTransfer = false
        reason = "No war selected"
      } else if (canTransfer) {
        const warField = deployAction.schema.find(
          (field) => field.name === "Target war",
        )
        const warAvailable = (warField as SelectField)?.options?.some(
          (option) => option.id === calculation.war,
        )
        if (!warAvailable) {
          canTransfer = false
          reason = "War not available for deployment"
        }
      }

      let unitsNeeded = []
      if (canTransfer && calculation.regularLegions > 0) {
        const deployed = getDeployedForces(
          publicGameState,
          calculation.commander,
          calculation.war,
        )
        const availableRegularLegions = publicGameState.legions.filter(
          (legion) =>
            !legion.veteran &&
            legion.campaign === null &&
            legion.allegiance === null,
        )
        const additionalLegionsNeeded =
          calculation.regularLegions -
          deployed.legions -
          (availableRegularLegions?.length ?? 0)

        if (additionalLegionsNeeded > 0) {
          unitsNeeded.push(
            `${additionalLegionsNeeded} more regular legion` +
              (additionalLegionsNeeded > 1 ? "s" : ""),
          )
        }
      }

      if (canTransfer && calculation.veteranLegions > 0) {
        const deployed = getDeployedForces(
          publicGameState,
          calculation.commander,
          calculation.war,
        )
        const availableVeteranLegions = publicGameState.legions.filter(
          (legion) =>
            legion.veteran &&
            legion.campaign === null &&
            legion.allegiance === null,
        )
        const additionalVeteransNeeded =
          calculation.veteranLegions -
          deployed.veteranLegions -
          (availableVeteranLegions?.length ?? 0)
        if (additionalVeteransNeeded > 0) {
          unitsNeeded.push(
            `${additionalVeteransNeeded} more veteran legion` +
              (additionalVeteransNeeded > 1 ? "s" : ""),
          )
        }
      }

      if (canTransfer && calculation.fleets > 0) {
        const deployed = getDeployedForces(
          publicGameState,
          calculation.commander,
          calculation.war,
        )
        const availableFleets = publicGameState.fleets.filter(
          (fleet) => fleet.campaign === null,
        )
        const additionalFleetsNeeded =
          calculation.fleets - deployed.fleets - (availableFleets?.length ?? 0)
        if (additionalFleetsNeeded > 0) {
          unitsNeeded.push(
            `${additionalFleetsNeeded} more fleet` +
              (additionalFleetsNeeded > 1 ? "s" : ""),
          )
        }
      }

      if (canTransfer && unitsNeeded.length > 0) {
        let text = ""
        for (let i = 0; i < unitsNeeded.length; i++) {
          if (i > 0 && i < unitsNeeded.length - 1) text += ","
          if (i > 0 && i === unitsNeeded.length - 1) text += " and"
          text += " " + unitsNeeded[i]
        }
        canTransfer = false
        reason = `Not enough forces in reserve (need ${text})`
      }

      return { canTransfer, isVisible: true, reason }
    },
    [privateGameState, publicGameState],
  )

  const selectedCalculation = allCalculations.find(
    (c) => c.id === selectedCalculationId,
  )
  const transferStatus = selectedCalculation
    ? getTransferStatus(selectedCalculation)
    : { canTransfer: false, isVisible: false, reason: "" }

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
          {allCalculations.map((calculation, index) => {
            const isProposal = calculation.id === "proposal"
            const isLastUserTab =
              !isProposal && index === allCalculations.length - 1
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
                {!isProposal && combatCalculations.length > 1 && (
                  <button
                    className="mr-1.5 flex h-5 w-5 items-center justify-center rounded-full text-xs text-neutral-700 hover:bg-neutral-200"
                    onClick={() => removeTab(calculation.id)}
                  >
                    ✕
                  </button>
                )}
              </div>
            )

            if (isLastUserTab) {
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

          {combatCalculations.length === 0 && (
            <div className="flex items-center gap-2">
              <button
                className="flex h-8 w-8 items-center justify-center rounded-full text-2xl hover:bg-neutral-200"
                onClick={addTab}
              >
                +
              </button>
            </div>
          )}
        </div>

        {allCalculations
          .sort((a, b) => {
            // Proposal always first
            if (a.id === "proposal") return -1
            if (b.id === "proposal") return 1
            // Then sort by id
            if (a.id == null && b.id == null) return 0
            if (a.id == null) return 1
            if (b.id == null) return -1
            return a.id - b.id
          })
          .map((calculation) => {
            const shouldDisplay =
              calculation.id === selectedCalculationId ||
              (selectedCalculationId === null && calculation.id === null)

            const isProposal = calculation.id === "proposal"

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
                  isReadOnly={isProposal}
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
          {transferStatus.isVisible && selectedCalculation && (
            <div className="group relative">
              <button
                type="button"
                onClick={() => onTransferToProposal(selectedCalculation)}
                disabled={!transferStatus.canTransfer}
                className="select-none rounded-md border border-blue-600 bg-white px-4 py-1 text-blue-600 hover:bg-blue-100 disabled:cursor-not-allowed disabled:border-neutral-400 disabled:text-neutral-400 disabled:hover:bg-white"
              >
                Transfer to proposal
              </button>
              {!transferStatus.canTransfer && transferStatus.reason && (
                <div className="absolute bottom-full left-1/2 z-10 mb-2 hidden w-max max-w-xs -translate-x-1/2 rounded bg-neutral-800 px-3 py-2 text-sm text-white shadow-lg group-hover:block">
                  {transferStatus.reason}
                  <div className="absolute left-1/2 top-full -mt-1 -translate-x-1/2 border-4 border-transparent border-t-neutral-800"></div>
                </div>
              )}
            </div>
          )}
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
          className="rounded-lg border border-neutral-400 bg-white shadow-lg"
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
