import SenatorPortrait from '@/components/SenatorPortrait'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import styles from './SenatorListItem.module.css'
import Office from '@/classes/Office'
import FactionIcon from './FactionIcon'

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
        <p><b>{props.senator.name}</b></p>
        <p>
          {factionNameAndUser ?
            <span><FactionIcon faction={props.faction} size={17} style={{marginRight: 8}} />Aligned to the {factionNameAndUser}</span>
            :
            'Unaligned'
          }
        </p>
      </div>
    </div>
  )
}

export default SenatorListItem
