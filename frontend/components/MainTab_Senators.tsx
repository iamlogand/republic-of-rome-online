import Stack from '@mui/material/Stack'

import Collection from '@/classes/Collection'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import SenatorListItem from '@/components/SenatorListItem'
import mainTabStyles from "./MainTab.module.css"
import Office from '@/classes/Office'

interface SenatorsTabProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
  offices: Collection<Office>
  setSelectedEntity: Function
}

// Tab containing a list of senators
const SenatorsTab = (props: SenatorsTabProps) => {
  return (
    <div className={mainTabStyles.tabContent}>
      <Stack direction="column" spacing={1} useFlexGap flexWrap="wrap">
        {props.senators.asArray.map((senator: FamilySenator) => {

          const faction = props.factions.asArray.find(f => f.id === senator.faction)
          const gameParticipant = props.gameParticipants.asArray.find(p => p.id === faction?.player)
          const office = props.offices.asArray.find(o => o.senator === senator.id) ?? null

          if (faction && gameParticipant) {
            return <SenatorListItem key={senator.id} gameParticipant={gameParticipant} faction={faction} senator={senator} office={office} setSelectedEntity={props.setSelectedEntity} />
          } else {
            return ""
          }
        })}
      </Stack>
    </div>
  )
}

export default SenatorsTab
