import SenatorPortrait from '@/components/senators/SenatorPortrait'
import Collection from '@/classes/Collection'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import styles from './SenatorListItem.module.css'

interface SenatorListItemProps {
  gameParticipant: GameParticipant
  faction: Faction
  senator: FamilySenator
}

// Item in the senator list
const SenatorListItem = (props: SenatorListItemProps) => {

  const factionNameAndUser = `${props.faction.getName()} Faction (${props.gameParticipant.user?.username})`

  return (
    <div key={props.senator.id} className={styles.senatorListItem}>
      <SenatorPortrait key={props.senator.id} senator={props.senator} faction={props.faction} />
      <div>
        <div><b>{props.senator.name}</b></div>
        <div>{factionNameAndUser ? `Aligned to the ${factionNameAndUser}` : 'Unaligned'}</div>
      </div>
    </div>
  )
}

export default SenatorListItem
