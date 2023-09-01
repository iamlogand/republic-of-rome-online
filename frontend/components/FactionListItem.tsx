import { useEffect, useState } from 'react'
import Stack from '@mui/material/Stack'

import SenatorPortrait from '@/components/SenatorPortrait'
import Collection from '@/classes/Collection'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import styles from './FactionListItem.module.css'
import FactionIcon from './FactionIcon'
import { useGameContext } from '@/contexts/GameContext'

interface FactionListItemProps {
  faction: Faction
}

// Item in the faction list
const FactionListItem = (props: FactionListItemProps) => {
  const { allPlayers, allSenators } = useGameContext()

  // Player that controls this faction
  const [player, setPlayer] = useState<Player | null>(null)
  useEffect(() => {
    setPlayer(allPlayers.byId[props.faction.player] ?? null)
  }, [allPlayers, props.faction, setPlayer])

  // Senators in this faction
  const [senators, setSenators] = useState<Collection<Senator>>(new Collection<Senator>())
  useEffect(() => {
    const senators = allSenators.asArray.filter(s => s.faction === props.faction.id).sort((a, b) => a.name.localeCompare(b.name))
    setSenators(new Collection<Senator>(senators))
  }, [allSenators, props.faction, setSenators])

  if (player && player.user && senators.allIds.length > 0) {
    return (
      <div className={styles.factionListItem}>
        <p>
          <span className={styles.factionIcon}>
            <FactionIcon faction={props.faction} size={17} selectable />
          </span>
          <b>{props.faction.getName()} Faction</b> of {player.user.username}
        </p>
        <p>This faction has {senators.allIds.length} aligned senators</p>
        <Stack direction="row" spacing={1}>
          {senators.asArray.map((senator: Senator) =>
            <SenatorPortrait key={senator.id} senator={senator} size={80} selectable />
          )}
        </Stack>
      </div>
    )
  } else {
    return null
  }
}

export default FactionListItem