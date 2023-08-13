import SenatorPortrait from '@/components/senators/SenatorPortrait'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import styles from './SenatorListItem.module.css'
import Office from '@/classes/Office'

interface SenatorListItemProps {
  gameParticipant: GameParticipant
  faction: Faction
  senator: FamilySenator
  office: Office | null
  setSelectedEntity: Function
}

// Item in the senator list
const SenatorListItem = (props: SenatorListItemProps) => {

  const factionNameAndUser = `${props.faction.getName()} Faction (${props.gameParticipant.user?.username})`

  return (
    <div key={props.senator.id} className={styles.senatorListItem}>
      <SenatorPortrait key={props.senator.id} senator={props.senator} faction={props.faction} office={props.office} size={80} setSelectedEntity={props.setSelectedEntity} clickable />
      <div>
        <div><b>{props.senator.name}</b></div>
        <div>{factionNameAndUser ? `Aligned to the ${factionNameAndUser}` : 'Unaligned'}</div>
      </div>
    </div>
  )
}

export default SenatorListItem
