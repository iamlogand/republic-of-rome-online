import { RefObject, useEffect, useState } from "react"

import SenatorPortrait from "@/components/SenatorPortrait"
import FamilySenator from "@/classes/FamilySenator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Senator.module.css"
import sectionStyles from "./DetailSection.module.css"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"

interface DetailSectionProps {
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a senator
const SenatorDetailSection = (props: DetailSectionProps) => {
  const { allPlayers, allFactions, allSenators, allOffices, selectedEntity } = useGameContext()
  
  // Selected senator
  const [senator, setSenator] = useState<FamilySenator | null>(null)
  useEffect(() => {
    if (selectedEntity) setSenator(allSenators.asArray.find(f => f.id === selectedEntity.id) ?? null)
  }, [allFactions, selectedEntity, allSenators, setSenator])
  
  // Faction that this senator is aligned to
  const [faction, setFaction] = useState<Faction | null>(null)
  useEffect(() => {
    if (senator) setFaction(allFactions.asArray.find(f => f.id === senator.faction) ?? null)
  }, [allFactions, senator, setFaction])
  
  // Player that controls this senator
  const [player, setPlayer] = useState<Player | null>(null)
  useEffect(() => {
    if (faction) setPlayer(allPlayers.asArray.find(p => p.id === faction.player) ?? null)
  }, [allPlayers, faction, setPlayer])

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
    const office = allOffices.asArray.find(o => o.senator === senator.id) ?? null

    return (
      <div className={sectionStyles.detailSectionInner}>
        <div className={styles.primaryArea}>
          <SenatorPortrait senator={senator} size={getPortraitSize()} />
          <div>
            <p><b>{senator!.name}</b></p>
            <p>
              {factionNameAndUser ?
                <span>
                  <span style={{marginRight: 8}}><FactionIcon faction={faction} size={17} clickable /></span>
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
