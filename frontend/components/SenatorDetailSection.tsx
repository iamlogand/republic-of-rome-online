import { RefObject, useEffect, useState } from "react"

import Collection from "@/classes/Collection"
import SenatorPortrait from "./senators/SenatorPortrait"
import FamilySenator from "@/classes/FamilySenator"
import GameParticipant from "@/classes/GameParticipant"
import Faction from "@/classes/Faction"
import Office from "@/classes/Office"
import styles from "./SenatorDetailSection.module.css"

interface DetailSectionProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
  offices: Collection<Office>
  selectedEntity: SelectedEntity | null
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a senator
const SenatorDetailSection = (props: DetailSectionProps) => {
  const [senator, setSenator] = useState<FamilySenator | null>(null)
  const [faction, setFaction] = useState<Faction | null>(null)
  const [gameParticipant, setGameParticipant] = useState<GameParticipant | null>(null)
  const [office, setOffice] = useState<Office | null>(null)
  
  // Get senator related data
  useEffect(() => {
    if (props.selectedEntity && props.selectedEntity.className === "FamilySenator") {
      setSenator(props.senators.asArray.find(s => s.id === props.selectedEntity?.id) ?? null)
      setFaction(props.factions.asArray.find(f => f.id === senator?.faction) ?? null)
      setGameParticipant(props.gameParticipants.asArray.find(p => p.id === faction?.player) ?? null)
      setOffice(props.offices.asArray.find(o => o.senator === senator?.id) ?? null)
    } else {
      setSenator(null)
      setFaction(null)
      setGameParticipant(null)
    }
  }, [props.selectedEntity, props.factions, props.gameParticipants, props.senators, props.offices, faction, senator])

  // Calculate senator portrait size.
  // Senator portrait size is determined by JavaScript rather than direct CSS,
  // so it necessary to do something like this to make the portrait responsive.
  const getPortraitSize = () => {
    const detailDivWidth = props.detailSectionRef.current?.offsetWidth
    if (detailDivWidth && detailDivWidth < 416) {
      return (detailDivWidth - 20) / 2
    } else {
      return 200
    }
  }
  
  if (faction && senator && gameParticipant) {
    const factionNameAndUser = `${faction.getName()} Faction (${gameParticipant.user?.username})`
    const office = props.offices.asArray.find(o => o.senator === senator.id) ?? null

    return (
      <div className={styles.detailSection}>
        <div className={styles.primaryArea}>
          <SenatorPortrait senator={senator} faction={faction} office={office} size={getPortraitSize()} />
          <div>
            <div><b>{senator!.name}</b></div>
            <div>{factionNameAndUser ? `Aligned to the ${factionNameAndUser}` : 'Unaligned'}</div>
          </div>
        </div>
        {office && <div>Serving as <b>{office?.name}</b></div>}
      </div>
    )
  } else {
    return null
  }
}

export default SenatorDetailSection
