import { useEffect, useState } from 'react'
import Stack from '@mui/material/Stack'

import SenatorPortrait from '@/components/SenatorPortrait'
import Collection from '@/classes/Collection'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import styles from './FactionListItem.module.css'
import { useGameContext } from '@/contexts/GameContext'
import FactionLink from '@/components/FactionLink'

interface FactionListItemProps {
  faction: Faction
}

// Item in the faction list
const FactionListItem = (props: FactionListItemProps) => {
  const { allPlayers, allSenators } = useGameContext()

  // Get faction-specific data
  const player = allPlayers.byId[props.faction.player] ?? null
  const senators = new Collection<Senator>(
    allSenators.asArray.filter(s => s.faction === props.faction.id).sort((a, b) => a.name.localeCompare(b.name)) ?? []
  )

  if (!player?.user || senators.allIds.length === 0) return null

  return (
    <div className={styles.factionListItem}>
      <p>
        <b><FactionLink faction={props.faction} includeIcon /></b> of {player.user.username}
      </p>
      <p>This faction has {senators.allIds.length} aligned senators</p>
      <div className={styles.portraits}>
        {senators.asArray.map((senator: Senator) =>
          <SenatorPortrait key={senator.id} senator={senator} size={80} selectable />
        )}
      </div>
    </div>
  )
}

export default FactionListItem