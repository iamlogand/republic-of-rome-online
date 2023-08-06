import Stack from '@mui/material/Stack'

import Collection from '@/classes/Collection'
import GameParticipant from '@/classes/GameParticipant'
import Faction from '@/classes/Faction'
import FamilySenator from '@/classes/FamilySenator'
import SenatorListItem from '@/components/SenatorListItem'

interface SenatorsTabProps {
  gameParticipants: Collection<GameParticipant>
  factions: Collection<Faction>
  senators: Collection<FamilySenator>
}

// Tab containing a list of senators
const SenatorsTab = (props: SenatorsTabProps) => {
  return (
    <>
      <Stack direction="column" spacing={1} useFlexGap flexWrap="wrap">
        {props.senators.asArray.map((senator: FamilySenator) => {

          const faction = props.factions.asArray.find(f => f.id === senator.faction)
          const gameParticipant = props.gameParticipants.asArray.find(p => p.id === faction?.player)

          if (faction && gameParticipant) {
            return <SenatorListItem key={senator.id} gameParticipant={gameParticipant} faction={faction} senator={senator} />
          } else {
            return ""
          }
        })}
      </Stack>
    </>
  )
}

export default SenatorsTab
