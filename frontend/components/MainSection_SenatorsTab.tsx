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
  
    return (
      <div key={key} style={style}>
        <SenatorListItem senator={senator} />
      </div>
    )
  }

  return (
    <div className={mainSectionStyles.tabContent}>
      <div className={mainSectionStyles.itemList}>
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
    </div>
  )
}

export default SenatorsTab
