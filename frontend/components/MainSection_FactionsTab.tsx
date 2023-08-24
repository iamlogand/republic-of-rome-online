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
    const isLastItem = index === allFactions.asArray.length - 1
    const adjustedHeight = isLastItem ? style.height : Number(style.height) - 10  // No gap after last item
  
    return (
      <div key={key} style={{...style, height: adjustedHeight}}>
        <FactionListItem faction={faction} />
      </div>
    )
  }

  return (
    <div className={mainSectionStyles.tabContent}>
      <AutoSizer>
        {({height, width}) => (
          <List
            width={width}
            height={height}
            rowCount={allFactions.asArray.length}
            rowHeight={200}
            rowRenderer={rowRenderer}
          />
        )}
      </AutoSizer>
    </div>
  );
}

export default FactionsTab
