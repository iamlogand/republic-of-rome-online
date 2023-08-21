import Stack from '@mui/material/Stack'

import FamilySenator from '@/classes/FamilySenator'
import SenatorListItem from '@/components/SenatorListItem'
import mainTabStyles from "./MainTab.module.css"
import { useGameContext } from '@/contexts/GameContext'

// Tab containing a list of senators
const SenatorsTab = () => {
  const { allSenators } = useGameContext()

  return (
    <div className={mainTabStyles.tabContent}>
      <Stack direction="column" spacing={1} useFlexGap flexWrap="wrap">
        {allSenators.asArray.map((senator: FamilySenator) =>
          <SenatorListItem key={senator.id} senator={senator} />
        )}
      </Stack>
    </div>
  )
}

export default SenatorsTab
