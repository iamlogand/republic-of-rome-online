import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSquare } from '@fortawesome/free-solid-svg-icons'

import Collection from "@/classes/Collection"
import PotentialAction from "@/classes/PotentialAction"
import styles from "./ProgressSection.module.css"
import Faction from "@/classes/Faction"
import GameParticipant from "@/classes/GameParticipant"
import Actions from "@/data/actions.json"

// JSON action data is typed so that it can be used in TypeScript
interface ActionType {
  sentence: string;
  title: string;
}

interface ActionsType {
  [key: string]: ActionType;
}

const typedActions: ActionsType = Actions;


interface ProgressSectionProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  potentialActions: Collection<PotentialAction>
}

// Progress section showing who players are waiting for
const ProgressSection = (props: ProgressSectionProps) => {

  const potentialActions = props.potentialActions.asArray.filter(a => a.required === true)

  if (potentialActions) {
    return (
      <section className={styles.progressSection}>
        {potentialActions.map((potentialAction) => {

          const faction = props.factions.asArray.find(f => f.id === potentialAction.faction)

          return (
            <div key={potentialAction.id}>
              <i>
                <FontAwesomeIcon icon={faSquare} fontSize={16} style={{marginRight: 8}} color={faction?.getColor()} />
                Waiting for {faction?.getName()} Faction to {typedActions[potentialAction.type]["sentence"]}
              </i>
            </div>
          )
        }
      )}
      </section>
    )
  } else {
    return null
  }
}

export default ProgressSection
