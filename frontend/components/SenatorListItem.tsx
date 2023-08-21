import { useState, useEffect } from 'react'

import SenatorPortrait from '@/components/SenatorPortrait'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import styles from './SenatorListItem.module.css'
import FactionIcon from './FactionIcon'
import { useGameContext } from '@/contexts/GameContext'

interface SenatorListItemProps {
  senator: FamilySenator
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
      <div>
        <p><b>{props.senator.name}</b></p>
        <p>
          {faction && player ?
            <span>
              <span style={{marginRight: 8}}><FactionIcon faction={faction} size={17} clickable /></span>
              Aligned to the {faction.getName()} Faction (${player.user?.username})
            </span>
            :
            'Unaligned'
          }
        </p>
      </div>
    </div>
  )
}

export default SenatorListItem
