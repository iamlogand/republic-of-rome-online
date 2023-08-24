import { List, ListRowProps } from 'react-virtualized';
import AutoSizer from 'react-virtualized-auto-sizer';

import SenatorListItem from '@/components/SenatorListItem'
import mainSectionStyles from "./MainSection.module.css"
import { useGameContext } from '@/contexts/GameContext'
import Senator from '@/classes/Senator';

// Tab containing a list of senators
const SenatorsTab = () => {
  const { allSenators } = useGameContext()

  // Function to render each row in the list
  const rowRenderer = ({ index, key, style }: ListRowProps) => {
    const senator: Senator = allSenators.asArray[index]
    const isLastItem = index === allSenators.asArray.length - 1
    const adjustedHeight = isLastItem ? style.height : Number(style.height) - 10  // No gap after last item
  
    return (
      <div key={key} style={{...style, height: adjustedHeight}}>
        <SenatorListItem senator={senator} />
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
            rowCount={allSenators.asArray.length}
            rowHeight={110}
            rowRenderer={rowRenderer}
          />
        )}
      </AutoSizer>
    </div>
  )
}

export default SenatorsTab
