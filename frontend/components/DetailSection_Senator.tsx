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

  const [senator, setSenator] = useState<FamilySenator | null>(null)
  const [faction, setFaction] = useState<Faction | null>(null)
  const [player, setPlayer] = useState<Player | null>(null)
  
  // Get senator related data
  useEffect(() => {
    if (selectedEntity && selectedEntity.className === "FamilySenator") {
      setSenator(allSenators.asArray.find(s => s.id === selectedEntity?.id) ?? null)
      setFaction(allFactions.asArray.find(f => f.id === senator?.faction) ?? null)
    } else {
      setSenator(null)
      setFaction(null)
    }
  }, [selectedEntity, allFactions, allSenators, allOffices, senator])
  
  useEffect(() => {
    if (selectedEntity && selectedEntity.className === "FamilySenator") {
      setPlayer(allPlayers.asArray.find(p => p.id === faction?.player) ?? null)
    }
  }, [selectedEntity, allPlayers, faction])

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
