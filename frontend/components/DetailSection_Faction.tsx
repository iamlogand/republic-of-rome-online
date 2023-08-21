import { useState, useEffect, RefObject } from "react"

import Stack from "@mui/material/Stack"

import Collection from "@/classes/Collection"
import FamilySenator from "@/classes/FamilySenator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Faction.module.css"
import sectionStyles from "./DetailSection.module.css"
import SenatorPortrait from "@/components/SenatorPortrait"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"

interface FactionDetailSectionProps {
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a faction
const FactionDetailSection = (props: FactionDetailSectionProps) => {
  const { allPlayers, allFactions, allSenators, allOffices, selectedEntity } = useGameContext()

  const [senators, setSenators] = useState<Collection<FamilySenator>>(new Collection<FamilySenator>())
  const [faction, setFaction] = useState<Faction | null>(null)
  const [player, setPlayer] = useState<Player | null>(null)

  // Get faction related data
  useEffect(() => {
    if (selectedEntity && selectedEntity.className === "Faction") {
      setSenators(new Collection<FamilySenator>(allSenators.asArray.filter(s => s.faction === selectedEntity?.id)))
      setFaction(allFactions.asArray.find(f => f.id === selectedEntity?.id) ?? null)
      
    } else {
      setSenators(new Collection<FamilySenator>())
      setFaction(null)
      setPlayer(null)
    }
  }, [selectedEntity, allFactions, allSenators, allOffices, faction])

  useEffect(() => {
    if (selectedEntity && selectedEntity.className === "Faction") {
      setPlayer(allPlayers.asArray.find(p => p.id === faction?.player) ?? null)
    }
  }, [selectedEntity, allPlayers, faction])

  if (faction && player) {
    return (
      <div className={sectionStyles.detailSectionInner}>
        <div className={styles.titleArea}>
          <span className={styles.factionIcon}>
            <FactionIcon faction={faction} size={30} />
          </span>
          <p><b>{faction.getName()} Faction</b> of {player.user?.username}</p>
        </div>
        <p>
          This faction has {senators.allIds.length} aligned senators
        </p>
        <Stack direction="row" spacing={1}>
          {senators.asArray.filter(p => p.faction === faction.id).map((senator: FamilySenator) =>
            <SenatorPortrait key={senator.id} senator={senator} size={80} clickable />
          )}
        </Stack>
      </div>
    )
  } else {
    return null
  }
}

export default FactionDetailSection
