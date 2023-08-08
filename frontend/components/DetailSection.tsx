import { useEffect, useRef, useState } from 'react'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faXmark } from '@fortawesome/free-solid-svg-icons'
import Button from '@mui/material/Button'

import FamilySenator from "@/classes/FamilySenator"
import SenatorPortrait from "./senators/SenatorPortrait"
import Collection from "@/classes/Collection"
import GameParticipant from "@/classes/GameParticipant"
import Faction from "@/classes/Faction"
import styles from "./DetailSection.module.css"

interface DetailSectionProps {
  senators: Collection<FamilySenator>
  factions: Collection<Faction>
  gameParticipants: Collection<GameParticipant>
  selectedEntity: SelectedEntity | null
  setSelectedEntity: Function
}

// Section showing details about selected entities
// Currently just works for senator
const DetailSection = (props: DetailSectionProps) => {
  const [senator, setSenator] = useState<FamilySenator | null>(null)
  const [faction, setFaction] = useState<Faction | null>(null)
  const [gameParticipant, setGameParticipant] = useState<GameParticipant | null>(null)
  const detailEntityRef = useRef<HTMLDivElement>(null);


  // Get senator related data
  useEffect(() => {
    if (props.selectedEntity && props.selectedEntity.className === "FamilySenator") {
      setSenator(props.senators.asArray.find(s => s.id === props.selectedEntity?.id) ?? null)
      setFaction(props.factions.asArray.find(f => f.id === senator?.faction) ?? null)
      setGameParticipant(props.gameParticipants.asArray.find(p => p.id === faction?.player) ?? null)
    } else {
      setSenator(null)
      setFaction(null)
      setGameParticipant(null)
    }
  }, [props.selectedEntity, props.senators, props.factions, props.gameParticipants, faction?.player, senator?.faction])

  // Senator portrait size
  const getPortraitSize = () => {
    const detailDivWidth = detailEntityRef.current?.offsetWidth
    console.log(detailDivWidth)
    if (detailDivWidth && detailDivWidth < 416) {
      return (detailDivWidth - 20) / 2
    } else {
      return 200
    }
  }
  
  // Clear button
  const handleClearDetails = () => {
    props.setSelectedEntity(null)
  }

  if (senator && faction && gameParticipant) {
    const factionNameAndUser = `${faction.getName()} Faction (${gameParticipant.user?.username})`
    return (
      <div className={styles.detailSection}>
        <div className={styles.header}>
          <b>Selected Senator</b>
          <Button size="small" onClick={handleClearDetails}>
            Clear <FontAwesomeIcon icon={faXmark} fontSize={16} style={{marginLeft: 8}} />
          </Button>
        </div>
        <div ref={detailEntityRef} className={styles.detailEntity}>
          <SenatorPortrait senator={senator} faction={faction} size={getPortraitSize()}/>
          <div>
            <div><b>{senator.name}</b></div>
            <div>{factionNameAndUser ? `Aligned to the ${factionNameAndUser}` : 'Unaligned'}</div>
          </div>
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