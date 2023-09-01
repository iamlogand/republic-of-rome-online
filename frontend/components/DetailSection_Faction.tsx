import { useState, useEffect, RefObject, useRef } from "react"

import { Card } from "@mui/material"

import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Faction.module.css"
import sectionStyles from "./DetailSection.module.css"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import SenatorList from "@/components/SenatorList"

interface FactionDetailsProps {
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a faction
const FactionDetails = (props: FactionDetailsProps) => {
  const { allPlayers, allFactions, allSenators, allTitles, selectedEntity } = useGameContext()

  const [senators, setSenators] = useState<Collection<Senator>>(new Collection<Senator>())
  const [faction, setFaction] = useState<Faction | null>(null)
  const [player, setPlayer] = useState<Player | null>(null)

  const sectionAreaRef = useRef(null)
  const mainAreaRef = useRef(null)

  // Get faction related data
  useEffect(() => {
    if (selectedEntity && selectedEntity.className === "Faction") {
      setSenators(new Collection<Senator>(allSenators.asArray.filter(s => s.faction === selectedEntity.id)))
      setFaction(allFactions.byId[selectedEntity.id] ?? null)
    } else {
      setSenators(new Collection<Senator>())
      setFaction(null)
      setPlayer(null)
    }
  }, [selectedEntity, allFactions, allSenators, allTitles, faction])

  useEffect(() => {
    if (faction && selectedEntity && selectedEntity.className === "Faction") {
      setPlayer(allPlayers.byId[faction.player] ?? null)
    }
  }, [selectedEntity, allPlayers, faction])

  if (faction && player) {
    return (
      <div ref={sectionAreaRef} className={styles.factionDetails}>
        <div className={styles.mainArea} ref={mainAreaRef}>
          <div className={styles.titleArea}>
            <span className={styles.factionIcon}>
              <FactionIcon faction={faction} size={30} />
            </span>
            <p><b>{faction.getName()} Faction</b> of {player.user?.username}</p>
          </div>
          <p>
            This faction has {senators.allIds.length} aligned senators
          </p>
        </div>
        <SenatorList faction={faction} selectableSenators minHeight={360} />
      </div>
    )
  } else {
    return null
  }
}

export default FactionDetails
