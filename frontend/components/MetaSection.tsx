import Link from 'next/link'

import Button from '@mui/material/Button'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faRightFromBracket } from '@fortawesome/free-solid-svg-icons'
import { faClock } from '@fortawesome/free-regular-svg-icons'

import Game from "@/classes/Game"
import Turn from "@/classes/Turn"
import Phase from "@/classes/Phase"
import Step from "@/classes/Step"
import styles from "./MetaSection.module.css"


interface MetaSectionProps {
  game: Game
  latestTurn: Turn | null
  latestPhase: Phase | null
  latestStep: Step | null
}

// Section showing meta info about the game
const MetaSection = (props: MetaSectionProps) => {
  if (props.latestTurn && props.latestPhase) {
    return (
      <section className={styles.metaSection}>
        <span>
          {props.game.name}
        </span>
        <span title={`Step ${props.latestStep?.index.toString()}`}>
          <FontAwesomeIcon icon={faClock} fontSize={16} style={{marginRight: 8}} />
          Turn {props.latestTurn.index}, {props.latestPhase.name} Phase
        </span>
        <div>
          <Button variant={"outlined"} LinkComponent={Link} href={`/games/${props.game.id}`}>
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
