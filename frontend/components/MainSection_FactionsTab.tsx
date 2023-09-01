import { List, ListRowProps } from 'react-virtualized';
import AutoSizer from 'react-virtualized-auto-sizer';

import Faction from '@/classes/Faction'
import FactionListItem from '@/components/FactionListItem'
import mainSectionStyles from "./MainSection.module.css"
import { useGameContext } from '@/contexts/GameContext'

// Tab containing a list of factions
const FactionsTab = () => {
  const { allFactions } = useGameContext()

  // Function to render each row in the list
  const rowRenderer = ({ index, key, style }: ListRowProps) => {
    const faction: Faction = allFactions.asArray[index]
  
    return (
      <div key={key} style={style}>
        <FactionListItem faction={faction} />
      </div>
    )
  }

  return (
    <div className={mainSectionStyles.tabContent}>
      <div className={mainSectionStyles.itemList}>
        <AutoSizer>
          {({height, width}: {height: number, width: number}) => (
            <List
              width={width}
              height={height}
              rowCount={allFactions.allIds.length}
              rowHeight={170}
              rowRenderer={rowRenderer}
            />
          )}
        </AutoSizer>
      </div>
    </div>
  );
}

export default FactionsTab
