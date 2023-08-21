import Collection from "@/classes/Collection"
import PotentialAction from "@/classes/PotentialAction"
import styles from "./ProgressSection.module.css"
import Actions from "@/data/actions.json"
import FactionIcon from './FactionIcon'
import { useGameContext } from '@/contexts/GameContext'

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
  potentialActions: Collection<PotentialAction>
}

// Progress section showing who players are waiting for
const ProgressSection = (props: ProgressSectionProps) => {
  const { allFactions } = useGameContext()

  const potentialActions = props.potentialActions.asArray.filter(a => a.required === true)

  if (potentialActions) {
    return (
      <section className={styles.progressSection}>
        {potentialActions.map((potentialAction) => {

          const faction = allFactions.asArray.find(f => f.id === potentialAction.faction) ?? null

          return (
            <div key={potentialAction.id} className={styles.actionItem}>
              <FactionIcon faction={faction} size={17} clickable />
              <p><i>Waiting for {faction?.getName()} Faction to {typedActions[potentialAction.type]["sentence"]}</i></p>
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
