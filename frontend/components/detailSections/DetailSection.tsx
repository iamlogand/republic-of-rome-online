import { useCallback, useEffect, useRef, useState } from "react"

import { IconButton } from "@mui/material"
import CloseIcon from "@mui/icons-material/Close"
import ArrowBackIcon from "@mui/icons-material/ArrowBack"

import SenatorDetailSection from "@/components/detailSections/DetailSection_Senator"
import FactionDetailSection from "@/components/detailSections/DetailSection_Faction"
import { useGameContext } from "@/contexts/GameContext"
import HraoTerm from "@/components/terms/Term_Hrao"
import RomeConsulTerm from "@/components/terms/Term_RomeConsul"
import SelectedDetail from "@/types/selectedDetail"

const BROWSING_HISTORY_LENGTH = 20

// Section showing details about selected entities
const DetailSection = () => {
  const { selectedDetail, setSelectedDetail } = useGameContext()
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
      // If current history has over 5 items, remove the first item
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

  // Go back to the previous detail using detail browsing history
  const goBack = useCallback(() => {
    setSelectedDetail(browsingHistory[browsingHistory.length - 2])
    setBrowsingHistory((currentHistory) => currentHistory.slice(0, -2))
  }, [browsingHistory, setSelectedDetail, setBrowsingHistory])

  if (!selectedDetail)
    return (
      <div className="h-full">
        <div className="p-2 h-full box-border flex justify-center items-center">
          <p>Nothing selected</p>
        </div>
      </div>
    )

  // Get the component for the selected term
  const getTermDetails = () => {
    switch (selectedDetail.name) {
      case "HRAO":
        return <HraoTerm />
      case "Rome Consul":
        return <RomeConsulTerm />
    }
  }

  return (
    <div className="box-border h-full flex flex-col bg-stone-50 rounded shadow">
      <div className="flex gap-2 justify-between items-center p-1 pl-2 border-0 border-b border-solid border-stone-200">
        <h3 className="leading-none m-0 ml-2 text-base text-stone-600">Selected {selectedDetail.id ? selectedDetail.type : "Term"}</h3>
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
        className="box-border h-full flex-1 overflow-y-auto bg-white rounded-b"
      >
        {selectedDetail.type === "Senator" && (
          <SenatorDetailSection detailSectionRef={detailSectionRef} />
        )}
        {selectedDetail.type === "Faction" && <FactionDetailSection />}
        {selectedDetail.type === "Term" && getTermDetails()}
      </div>
    </div>
  )
}

export default DetailSection
