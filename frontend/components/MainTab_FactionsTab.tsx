import Stack from '@mui/material/Stack'

import Collection from '@/classes/Collection'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import FactionListItem from '@/components/FactionListItem'
import mainTabStyles from "./MainTab.module.css"
import Office from '@/classes/Office'

interface FactionsTabProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
  offices: Collection<Office>
  setSelectedEntity: Function
}

// Tab containing a list of factions
const FactionsTab = (props: FactionsTabProps) => {
  return (
    <div className={mainTabStyles.tabContent}>
      <Stack direction="column" spacing={1} useFlexGap flexWrap="wrap">
        {props.factions.asArray.map((faction: Faction) => {

          const gameParticipant = props.gameParticipants.asArray.find(p => p.id === faction.player)

          // Filter to only include senators and offices held by those senators
          const senators = new Collection<FamilySenator>(props.senators.asArray.filter(s => s.faction === faction.id))
          const offices = new Collection<Office>(props.offices.asArray.filter(o => senators.allIds.includes(o.senator)))
          
          if (gameParticipant && senators) {
            return <FactionListItem key={faction.id} gameParticipant={gameParticipant} faction={faction} senators={senators} offices={offices} setSelectedEntity={props.setSelectedEntity} />
          } else {
            return ""
          }
        })}
      </Stack>
    </div>
  )
}

export default FactionsTab
