import { useCallback, useEffect, useRef, useState } from "react"

import { IconButton } from "@mui/material"
import CloseIcon from "@mui/icons-material/Close"
import ArrowBackIcon from "@mui/icons-material/ArrowBack"

import SenatorDetailSection from "@/components/entityDetails/EntityDetail_Senator"
import FactionDetailSection from "@/components/entityDetails/EntityDetail_Faction"
import { useGameContext } from "@/contexts/GameContext"
import HraoTerm from "@/components/terms/Term_Hrao"
import RomeConsulTerm from "@/components/terms/Term_RomeConsul"
import SelectedDetail from "@/types/SelectedDetail"
import PriorConsulTerm from "@/components/terms/Term_PriorConsul"
import FactionTerm from "@/components/terms/Term_Faction"
import SecretTerm from "@/components/terms/Term_Secret"
import SenatorTerm from "@/components/terms/Term_Senator"
import MortalityPhaseTerm from "@/components/terms/Term_MortalityPhase"
import ForumPhaseTerm from "@/components/terms/Term_ForumPhase"
import RevolutionPhaseTerm from "@/components/terms/Term_RevolutionPhase"
import CombatPhaseTerm from "@/components/terms/Term_CombatPhase"
import PopulationPhaseTerm from "@/components/terms/Term_PopulationPhase"
import RevenuePhaseTerm from "@/components/terms/Term_RevenuePhase"
import SenatePhaseTerm from "@/components/terms/Term_SenatePhase"
import TurnTerm from "@/components/terms/Term_Turn"
import FactionPhaseTerm from "@/components/terms/Term_FactionPhase"
import FinalForumPhaseTerm from "@/components/terms/Term_FinalForumPhase"

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
      case "Combat Phase":
        return <CombatPhaseTerm />
      case "Faction":
        return <FactionTerm />
      case "Faction Phase":
        return <FactionPhaseTerm />
      case "Final Forum Phase":
        return <FinalForumPhaseTerm />
      case "Forum Phase":
        return <ForumPhaseTerm />
      case "HRAO":
        return <HraoTerm />
      case "Mortality Phase":
        return <MortalityPhaseTerm />
      case "Population Phase":
        return <PopulationPhaseTerm />
      case "Prior Consul":
        return <PriorConsulTerm />
      case "Revenue Phase":
        return <RevenuePhaseTerm />
      case "Revolution Phase":
        return <RevolutionPhaseTerm />
      case "Rome Consul":
        return <RomeConsulTerm />
      case "Secret":
        return <SecretTerm />
      case "Senate Phase":
        return <SenatePhaseTerm />
      case "Senator":
        return <SenatorTerm />
      case "Turn":
        return <TurnTerm />
    }
  }

  return (
    <div className="box-border h-full flex flex-col bg-neutral-50 dark:bg-neutral-700 rounded shadow">
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
          <SenatorDetailSection detailSectionRef={detailSectionRef} />
        )}
        {selectedDetail.type === "Faction" && <FactionDetailSection />}
        {selectedDetail.type === "Term" && getTermDetails()}
      </div>
    </div>
  )
}

export default DetailSection
