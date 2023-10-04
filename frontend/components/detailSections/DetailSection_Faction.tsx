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
  const { allPlayers, allFactions, allSenators, selectedDetail } =
    useGameContext()

  // Get faction-specific data
  let senators: Collection<Senator> = new Collection<Senator>([])
  if (selectedDetail && selectedDetail.type == "Faction") {
    senators = new Collection<Senator>(
      allSenators.asArray.filter((s) => s.faction === selectedDetail.id)
    )
  }
  const faction: Faction | null = selectedDetail?.id
    ? allFactions.byId[selectedDetail.id] ?? null
    : null
  const player: Player | null = faction?.player
    ? allPlayers.byId[faction.player] ?? null
    : null

  // If there is no faction selected, render nothing
  if (!faction || !player) return null

  return (
    <div className={styles.factionDetails}>
      <div className={styles.mainArea}>
        <div className={styles.titleArea}>
          <span className={styles.factionIcon}>
            <FactionIcon faction={faction} size={26} />
          </span>
          <h4>
            <b>{faction.getName()} Faction</b> of {player.user?.username}
          </h4>
        </div>
        <p>This faction has {senators.allIds.length} aligned senators</p>
      </div>
      <SenatorList faction={faction} selectableSenators />
    </div>
  )
}

export default FactionDetails
