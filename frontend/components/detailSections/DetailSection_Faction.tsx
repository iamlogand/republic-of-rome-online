import { useRef } from "react"

import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Faction.module.css"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import SenatorList from "@/components/SenatorList"

// Detail section content for a faction
const FactionDetails = () => {
  const { allPlayers, allFactions, allSenators, selectedEntity  } = useGameContext()

  const sectionAreaRef = useRef(null)
  const mainAreaRef = useRef(null)

  let senators: Collection<Senator> = new Collection<Senator>([])
  if (selectedEntity && selectedEntity.className == "Faction") {
    senators = new Collection<Senator>(allSenators.asArray.filter(s => s.faction === selectedEntity.id))
  }
  const faction: Faction | null = selectedEntity?.id ? allFactions.byId[selectedEntity.id] ?? null : null
  const player: Player | null = faction?.player ? allPlayers.byId[faction.player] ?? null : null

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
