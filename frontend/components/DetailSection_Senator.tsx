import { RefObject, useEffect, useState } from "react"

import Collection from "@/classes/Collection"
import SenatorPortrait from "@/components/SenatorPortrait"
import FamilySenator from "@/classes/FamilySenator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import Office from "@/classes/Office"
import styles from "./DetailSection_Senator.module.css"
import sectionStyles from "./DetailSection.module.css"
import FactionIcon from "@/components/FactionIcon"
import SelectedEntity from "@/types/selectedEntity"

interface DetailSectionProps {
  players: Collection<Player>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
  offices: Collection<Office>
  selectedEntity: SelectedEntity | null
  detailSectionRef: RefObject<HTMLDivElement>
  setSelectedEntity: Function
}

// Detail section content for a senator
const SenatorDetailSection = (props: DetailSectionProps) => {
  const [senator, setSenator] = useState<FamilySenator | null>(null)
  const [faction, setFaction] = useState<Faction | null>(null)
  const [player, setPlayer] = useState<Player | null>(null)
  
  // Get senator related data
  useEffect(() => {
    if (props.selectedEntity && props.selectedEntity.className === "FamilySenator") {
      setSenator(props.senators.asArray.find(s => s.id === props.selectedEntity?.id) ?? null)
      setFaction(props.factions.asArray.find(f => f.id === senator?.faction) ?? null)
    } else {
      setSenator(null)
      setFaction(null)
    }
  }, [props.selectedEntity, props.factions, props.senators, props.offices, senator])
  
  useEffect(() => {
    if (props.selectedEntity && props.selectedEntity.className === "FamilySenator") {
      setPlayer(props.players.asArray.find(p => p.id === faction?.player) ?? null)
    }
  }, [props.selectedEntity, props.players, faction])

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
  
  if (faction && senator && player) {
    const factionNameAndUser = `${faction.getName()} Faction (${player.user?.username})`
    const office = props.offices.asArray.find(o => o.senator === senator.id) ?? null

    return (
      <div className={sectionStyles.detailSectionInner}>
        <div className={styles.primaryArea}>
          <SenatorPortrait senator={senator} faction={faction} office={office} size={getPortraitSize()} />
          <div>
            <p><b>{senator!.name}</b></p>
            <p>
              {factionNameAndUser ?
                <span>
                  <span style={{marginRight: 8}}><FactionIcon faction={faction} size={17} setSelectedEntity={props.setSelectedEntity} /></span>
                  Aligned to the {factionNameAndUser}
                </span>
                :
                'Unaligned'
              }
            </p>
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
