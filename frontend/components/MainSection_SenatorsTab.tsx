import Image from 'next/image'
import { List, ListRowProps } from 'react-virtualized';
import AutoSizer from 'react-virtualized-auto-sizer';

import SenatorListItem from '@/components/SenatorListItem'
import mainSectionStyles from "./MainSection.module.css"
import { useGameContext } from '@/contexts/GameContext'
import Senator from '@/classes/Senator';
import styles from "./MainSection_SenatorsTab.module.css"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"

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
      <div className={styles.headers}>
        <div><Image src={MilitaryIcon} height={34} width={34} alt="Military Icon" /></div>
        <div><Image src={OratoryIcon} height={34} width={34} alt="Oratory Icon" /></div>
        <div><Image src={LoyaltyIcon} height={34} width={34} alt="Loyalty Icon" /></div>
        <div><Image src={InfluenceIcon} height={34} width={34} alt="Influence Icon" /></div>
        <div><Image src={TalentsIcon} height={34} width={34} alt="Talents Icon" /></div>
        <div><Image src={TalentsIcon} height={34} width={34} alt="Influence Icon" /></div> {/* TODO Replace with popularity icon*/}
        <div><Image src={TalentsIcon} height={34} width={34} alt="Talents Icon" /></div> {/* TODO Replace with knights icon*/}
      </div>
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
