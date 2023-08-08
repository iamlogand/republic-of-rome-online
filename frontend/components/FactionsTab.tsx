import Stack from '@mui/material/Stack';

import Collection from '@/classes/Collection';
import GameParticipant from '@/classes/GameParticipant';
import Faction from '@/classes/Faction';
import FamilySenator from '@/classes/FamilySenator';
import FactionListItem from '@/components/FactionListItem';

interface FactionsTabProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
  setSelectedEntity: Function
}

// Tab containing a list of factions
const FactionsTab = (props: FactionsTabProps) => {
  return (
    <>
      <Stack direction="column" spacing={1} useFlexGap flexWrap="wrap">
        {props.factions.asArray.map((faction: Faction) => {

          const gameParticipant = props.gameParticipants.asArray.find(p => p.id === faction.player)
          const senators = new Collection<FamilySenator>(props.senators.asArray.filter(s => s.faction === faction.id))
          
          if (gameParticipant && senators) {
            return <FactionListItem key={faction.id} gameParticipant={gameParticipant} faction={faction} senators={senators} setSelectedEntity={props.setSelectedEntity} />
          } else {
            return ""
          }
        })}
      </Stack>
    </>
  )
}

export default FactionsTab
