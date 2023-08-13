import { useLayoutEffect, useRef, useState } from 'react'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faXmark } from '@fortawesome/free-solid-svg-icons'
import Button from '@mui/material/Button'

import FamilySenator from "@/classes/FamilySenator"
import Collection from "@/classes/Collection"
import GameParticipant from "@/classes/GameParticipant"
import Faction from "@/classes/Faction"
import Office from "@/classes/Office"
import styles from "./DetailSection.module.css"
import SenatorDetailSection from './SenatorDetailSection'

interface DetailSectionProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
  offices: Collection<Office>
  selectedEntity: SelectedEntity | null
  setSelectedEntity: Function
}

// Section showing details about selected entities
// Currently just works for senator
const DetailSection = (props: DetailSectionProps) => {
  const detailSectionRef = useRef<HTMLDivElement>(null);
  
  // Clear button
  const handleClearDetails = () => {
    props.setSelectedEntity(null)
  }

  // Get the user-facing entity name
  const getEntityName = () => {
    switch (props.selectedEntity?.className) {
      case "FamilySenator":
        return "Senator"
    }
  }

  if (props.selectedEntity) {
    return (
      <div className={styles.detailSection}>
        <div className={styles.header}>
          <b>Selected {getEntityName()}</b>
          <Button size="small" onClick={handleClearDetails}>
            Clear <FontAwesomeIcon icon={faXmark} fontSize={16} style={{marginLeft: 8}} />
          </Button>
        </div>
        <div ref={detailSectionRef}>
          <SenatorDetailSection
            gameParticipants={props.gameParticipants}
            factions={props.factions}
            senators={props.senators}
            offices={props.offices}
            selectedEntity={props.selectedEntity}
            detailSectionRef={detailSectionRef}/>
        </div>
      </div>
    )
  } else {
    return (
      <div className={styles.nothing}>
        <div>Nothing selected</div>
      </div>
    )
  }
}

export default DetailSection
