import { useEffect, useState } from 'react'
import Link from 'next/link'

import Button from '@mui/material/Button'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRightFromBracket } from '@fortawesome/free-solid-svg-icons'
import { faClock } from '@fortawesome/free-regular-svg-icons'

import Turn from "@/classes/Turn"
import Phase from "@/classes/Phase"
import styles from "./MetaSection.module.css"
import { useGameContext } from '@/contexts/GameContext'
import { useAuthContext } from '@/contexts/AuthContext'
import Faction from '@/classes/Faction'
import FactionLink from '@/components/FactionLink'


interface MetaSectionProps {
  latestTurn: Turn | null
  latestPhase: Phase | null
}

// Section showing meta info about the game
const MetaSection = (props: MetaSectionProps) => {
  const { user } = useAuthContext()
  const { game, latestStep, allPlayers, allFactions } = useGameContext()

  const [faction, setFaction] = useState<Faction | null>(null)

  // Update faction
  useEffect(() => {
    const player = allPlayers.asArray.find(p => p.user?.id === user?.id)
    const faction = allFactions.asArray.find(f => f.player === player?.id)
    if (faction) setFaction(faction)
  }, [user, allPlayers, allFactions])

  if (game && latestStep && props.latestTurn && props.latestPhase) {
    return (
      <section className={styles.metaSection}>
        <h2>{game.name}</h2>
        <span title={`Step ${latestStep?.index.toString()}`}>
          <FontAwesomeIcon icon={faClock} fontSize={16} style={{marginRight: 8}} />
          Turn {props.latestTurn.index}, {props.latestPhase.name} Phase
        </span>
        {faction && 
          <span>Playing as the <FactionLink faction={faction} includeIcon /></span>
        }
        <div>
          <Button variant={"outlined"} LinkComponent={Link} href={`/games/${game.id}`}>
            <FontAwesomeIcon icon={faRightFromBracket} fontSize={16} style={{marginRight: 8}} />Lobby
          </Button>
        </div>
      </section>
    )
  } else {
    return null
  }
}

export default MetaSection
