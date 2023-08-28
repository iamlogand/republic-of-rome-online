import { useState, useEffect } from 'react'

import SenatorPortrait from '@/components/SenatorPortrait'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import styles from './SenatorListItem.module.css'
import FactionIcon from './FactionIcon'
import { useGameContext } from '@/contexts/GameContext'
import skillsJSON from "@/data/skills.json"

interface SenatorListItemProps {
  senator: Senator
}

// Item in the senator list
const SenatorListItem = (props: SenatorListItemProps) => {
  const { allPlayers, allFactions, allOffices } = useGameContext()
 
  // Faction that this senator is aligned to
  const [faction, setFaction] = useState<Faction | null>(null)
  useEffect(() => {
    setFaction(allFactions.asArray.find(f => f.id === props.senator.faction) ?? null)
  }, [allFactions, props.senator, setFaction])

  // Player that controls this senator
  const [player, setPlayer] = useState<Player | null>(null)
  useEffect(() => {
    if (faction) setPlayer(allPlayers.asArray.find(p => p.id === faction.player) ?? null)
  }, [allPlayers, faction, setFaction])

  return (
    <div key={props.senator.id} className={styles.senatorListItem}>
      <SenatorPortrait senator={props.senator} size={80} clickable />
      <div className={styles.primaryArea}>
        <p><b>{props.senator.name}</b></p>
        <p>
          {faction && player ?
            <span>
              <span style={{marginRight: 8}}><FactionIcon faction={faction} size={17} clickable /></span>
              {faction.getName()} Faction ({player.user?.username})
            </span>
            :
            'Unaligned'
          }
        </p>
        <div className={styles.attributeListContainer}>
          <div className={styles.attributeList}>
            <div style={{
              backgroundColor: skillsJSON.colors.number["military"],
              boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number["military"]}`
            }}>
              {props.senator.military}
            </div>
            <div style={{
              backgroundColor: skillsJSON.colors.number["oratory"],
              boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number["oratory"]}`
            }}>
              {props.senator.oratory}
            </div>
            <div style={{
              backgroundColor: skillsJSON.colors.number["loyalty"],
              boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number["loyalty"]}`
            }}>
              {props.senator.loyalty}
            </div>
            <div>{props.senator.influence}</div>
            <div>{props.senator.talents}</div>
            <div>{props.senator.popularity}</div>
            <div>{props.senator.knights}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SenatorListItem
