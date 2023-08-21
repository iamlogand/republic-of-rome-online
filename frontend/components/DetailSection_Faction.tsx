import { useState, useEffect, RefObject } from "react"

import Stack from "@mui/material/Stack"

import Collection from "@/classes/Collection"
import FamilySenator from "@/classes/FamilySenator"
import GameParticipant from "@/classes/GameParticipant"
import Faction from "@/classes/Faction"
import Office from "@/classes/Office"
import SelectedEntity from "@/types/selectedEntity"
import styles from "./DetailSection_Faction.module.css"
import sectionStyles from "./DetailSection.module.css"
import SenatorPortrait from "@/components/SenatorPortrait"
import FactionIcon from "@/components/FactionIcon"

interface FactionDetailSectionProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
  offices: Collection<Office>
  selectedEntity: SelectedEntity | null
  detailSectionRef: RefObject<HTMLDivElement>
  setSelectedEntity: Function
}

// Detail section content for a faction
const FactionDetailSection = (props: FactionDetailSectionProps) => {
  const [senators, setSenators] = useState<Collection<FamilySenator>>(new Collection<FamilySenator>())
  const [faction, setFaction] = useState<Faction | null>(null)
  const [gameParticipant, setGameParticipant] = useState<GameParticipant | null>(null)

  // Get faction related data
  useEffect(() => {
    if (props.selectedEntity && props.selectedEntity.className === "Faction") {
      setSenators(new Collection<FamilySenator>(props.senators.asArray.filter(s => s.faction === props.selectedEntity?.id)))
      setFaction(props.factions.asArray.find(f => f.id === props.selectedEntity?.id) ?? null)
      
    } else {
      setSenators(new Collection<FamilySenator>())
      setFaction(null)
      setGameParticipant(null)
    }
  }, [props.selectedEntity, props.factions, props.gameParticipants, props.senators, props.offices, faction])

  useEffect(() => {
    if (props.selectedEntity && props.selectedEntity.className === "Faction") {
      setGameParticipant(props.gameParticipants.asArray.find(p => p.id === faction?.player) ?? null)
    }
  }, [faction])

  if (faction && gameParticipant) {
    return (
      <div className={sectionStyles.detailSectionInner}>
        <div className={styles.titleArea}>
          <span className={styles.factionIcon}>
            <FactionIcon faction={faction} size={30} />
          </span>
          <p><b>{faction.getName()} Faction</b> of {gameParticipant.user?.username}</p>
        </div>
        <p>
          This faction has {senators.allIds.length} aligned senators
        </p>
        <Stack direction="row" spacing={1}>
          {senators.asArray.filter(p => p.faction === faction.id).map((senator: FamilySenator) => {
            const office = props.offices.asArray.find(o => o.senator === senator.id) ?? null
            return <SenatorPortrait key={senator.id} senator={senator} faction={faction} office={office} size={80} setSelectedEntity={props.setSelectedEntity} />
          })}
        </Stack>
      </div>
    )
  } else {
    return null
  }
}

export default FactionDetailSection
