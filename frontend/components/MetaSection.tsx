import Link from 'next/link'

import Button from '@mui/material/Button'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRightFromBracket } from '@fortawesome/free-solid-svg-icons'
import { faClock } from '@fortawesome/free-regular-svg-icons'

import Turn from "@/classes/Turn"
import Phase from "@/classes/Phase"
import styles from "./MetaSection.module.css"
import { useGameContext } from '@/contexts/GameContext'


interface MetaSectionProps {
  latestTurn: Turn | null
  latestPhase: Phase | null
}

// Section showing meta info about the game
const MetaSection = (props: MetaSectionProps) => {
  const { game, latestStep } = useGameContext()

  if (game && latestStep && props.latestTurn && props.latestPhase) {
    return (
      <section className={styles.metaSection}>
        <span>
          {game.name}
        </span>
        <span title={`Step ${latestStep?.index.toString()}`}>
          <FontAwesomeIcon icon={faClock} fontSize={16} style={{marginRight: 8}} />
          Turn {props.latestTurn.index}, {props.latestPhase.name} Phase
        </span>
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
