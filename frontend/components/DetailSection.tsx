import { ReactNode, useCallback, useEffect, useRef, useState } from "react"

import { IconButton } from "@mui/material"
import CloseIcon from "@mui/icons-material/Close"
import ArrowBackIcon from "@mui/icons-material/ArrowBack"

import SenatorDetails from "@/components/entityDetails/SenatorDetails"
import FactionDetails from "@/components/entityDetails/FactionDetails"
import { useGameContext } from "@/contexts/GameContext"
import SelectedDetail from "@/types/SelectedDetail"
import terms from "@/componentTables/termComponents"
import { useCookieContext } from "@/contexts/CookieContext"

const BROWSING_HISTORY_LENGTH = 100

// Section showing details about selected entities
const DetailSection = () => {
  const { darkMode } = useCookieContext()
  const { selectedDetail, setSelectedDetail, sameSelectionCounter } =
    useGameContext()
  const detailSectionRef = useRef<HTMLDivElement>(null)
  const [browsingHistory, setBrowsingHistory] = useState<SelectedDetail[]>([])

  // Update detail browsing history when selected detail changes
  useEffect(() => {
    // If no selected detail, clear browsing history
    if (!selectedDetail) {
      setBrowsingHistory([])
      return
    }
    setBrowsingHistory((currentHistory) => {
      // If current history has over too many items, remove the first item
      currentHistory =
        currentHistory.length >= BROWSING_HISTORY_LENGTH
          ? currentHistory.slice(1)
          : currentHistory
      const lastItem = currentHistory[currentHistory.length - 1]
      // Prevent duplicate items being added back to back
      if (
        lastItem?.type === selectedDetail?.type &&
        lastItem?.id === selectedDetail?.id &&
        lastItem?.name === selectedDetail?.name
      ) {
        return currentHistory
      }
      return [...currentHistory, selectedDetail]
    })
  }, [selectedDetail])

  // Flash the detail section when an already selected item is selected again
  const [flash, setFlash] = useState(false)
  useEffect(() => {
    setFlash(true)
    const timer = setTimeout(() => setFlash(false), 800) // adjust timing as needed
    return () => clearTimeout(timer)
  }, [sameSelectionCounter])

  // Go back to the previous detail using detail browsing history
  const goBack = useCallback(() => {
    setSelectedDetail(browsingHistory[browsingHistory.length - 2])
    setBrowsingHistory((currentHistory) => currentHistory.slice(0, -2))
  }, [browsingHistory, setSelectedDetail, setBrowsingHistory])

  // Scroll to the top of the detail section when a new item is selected
  useEffect(() => {
    if (detailSectionRef.current) {
      detailSectionRef.current.scrollTop = 0
    }
  }, [selectedDetail])

  if (!selectedDetail)
    return (
      <div className="h-full">
        <div className="p-2 h-full box-border flex justify-center items-center">
          <p>Nothing selected</p>
        </div>
      </div>
    )

  // Get the component for the selected term
  const getTermDetails = () => terms[selectedDetail.name] as ReactNode

  return (
    <div
      className={`${
        flash ? (darkMode ? "darkModeFlash" : "lightModeFlash") : ""
      } box-border h-full flex flex-col bg-neutral-50 dark:bg-neutral-700 rounded shadow outline-offset-[-2px]`}
    >
      <div className="flex gap-2 justify-between items-center p-1 pl-2 border-0 border-b border-solid border-neutral-200 dark:border-neutral-750">
        <h3 className="leading-none m-0 ml-2 text-base text-neutral-600 dark:text-neutral-100">
          Selected {selectedDetail.id ? selectedDetail.type : "Term"}
        </h3>
        <div>
          <IconButton
            aria-label="back"
            onClick={goBack}
            disabled={browsingHistory.length > 1 ? false : true}
          >
            <ArrowBackIcon />
          </IconButton>
          <IconButton
            aria-label="close"
            onClick={() => setSelectedDetail(null)}
          >
            <CloseIcon />
          </IconButton>
        </div>
      </div>
      <div
        ref={detailSectionRef}
        className="box-border h-full flex-1 overflow-y-auto bg-white dark:bg-neutral-600 rounded-b"
      >
        {selectedDetail.type === "Senator" && (
          <SenatorDetails detailSectionRef={detailSectionRef} />
        )}
        {selectedDetail.type === "Faction" && <FactionDetails />}
        {selectedDetail.type === "Term" && getTermDetails()}
      </div>
    </div>
  )
}

export default DetailSection
