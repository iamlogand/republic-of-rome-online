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
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import FactionLink from '@/components/FactionLink'
import SenatorLink from '@/components/SenatorLink'
import { Tooltip } from '@mui/material'


interface MetaSectionProps {
  latestTurn: Turn | null
  latestPhase: Phase | null
}

// Section showing meta info about the game
const MetaSection = (props: MetaSectionProps) => {
  const { user } = useAuthContext()
  const { game, latestStep, allPlayers, allFactions, allSenators } = useGameContext()

  // Get data
  const player: Player | null = user?.id ? allPlayers.asArray.find(p => p.user?.id === user?.id) ?? null : null
  const faction: Faction | null = player?.id ? allFactions.asArray.find(f => f.player === player?.id) ?? null : null
  const hrao: Senator | null = allSenators.asArray.find(s => s.rank === 0) ?? null
  const hraoFaction: Faction | null = hrao?.faction ? allFactions.asArray.find(f => f.id == hrao.faction) ?? null : null

  if (game && latestStep && props.latestTurn && props.latestPhase) {
    return (
      <section className={styles.metaSection}>
        <div className={styles.nameAndTurn}>
          <div>
            <h2>{game.name}</h2>
            <span title={`Step ${latestStep?.index.toString()}`} style={{ fontSize: 14 }}>
              <FontAwesomeIcon icon={faClock} fontSize={14} style={{marginRight: 4}} />
              Turn {props.latestTurn.index}, {props.latestPhase.name} Phase
            </span>
          </div>
          <div className={styles.lobbyButton}>
            <Button variant="outlined" LinkComponent={Link} href={`/games/${game.id}`}>
              <FontAwesomeIcon icon={faRightFromBracket} fontSize={16} style={{marginRight: 8}} />Lobby
            </Button>
          </div>
        </div>
        <div className={styles.otherInfo}>
          {faction && <div><span>Playing as the <FactionLink faction={faction} includeIcon /></span></div>}
          {hrao &&
            <div>
              <span>
                The <Tooltip title="Highest Ranking Available Officer" enterDelay={500} arrow><span>HRAO</span></Tooltip> is <SenatorLink senator={hrao} />
                {hraoFaction && <span> of <FactionLink faction={hraoFaction} includeIcon /></span>}
              </span>
            </div>
          }
        </div>
      </section>
    )
  } else {
    return null
  }
}

export default MetaSection
