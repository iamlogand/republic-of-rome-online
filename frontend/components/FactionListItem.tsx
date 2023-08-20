import Stack from '@mui/material/Stack'
import SenatorPortrait from '@/components/SenatorPortrait'
import Collection from '@/classes/Collection'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import styles from './FactionListItem.module.css'
import Office from '@/classes/Office'

interface FactionListItemProps {
  gameParticipant: GameParticipant
  faction: Faction
  senators: Collection<FamilySenator>
  offices: Collection<Office>
  setSelectedEntity: Function
}

// Item in the faction list
const FactionListItem = (props: FactionListItemProps) => {

  return (
    <div className={styles.factionListItem}>
      <p className={styles.paragraph}>
        <b>{props.faction.getName()} Faction</b> of {props.gameParticipant.user?.username}
      </p>
      <p className={styles.paragraph}>
        This faction has {props.senators.allIds.length} aligned senators
      </p>
      <Stack direction="row" spacing={1}>
        {props.senators.asArray.filter(p => p.faction === props.faction.id).map((senator: FamilySenator) => {
          const office = props.offices.asArray.find(o => o.senator === senator.id) ?? null
          return <SenatorPortrait key={senator.id} senator={senator} faction={props.faction} office={office} size={80} setSelectedEntity={props.setSelectedEntity} clickable />
        })}
      </Stack>
    </div>
  )
}

export default FactionListItem