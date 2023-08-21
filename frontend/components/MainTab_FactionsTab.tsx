import Stack from '@mui/material/Stack'

import Faction from '@/classes/Faction'
import FactionListItem from '@/components/FactionListItem'
import mainTabStyles from "./MainTab.module.css"
import { useGameContext } from '@/contexts/GameContext'

// Tab containing a list of factions
const FactionsTab = () => {
  const { allFactions } = useGameContext()
  
  return (
    <div className={mainTabStyles.tabContent}>
      <Stack direction="column" spacing={1} useFlexGap flexWrap="wrap">
        {allFactions.asArray.map((faction: Faction) => {
          return <FactionListItem key={faction.id} faction={faction} />
        })}
      </Stack>
    </div>
  )
}

export default FactionsTab
