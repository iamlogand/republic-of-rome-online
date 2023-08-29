import { useEffect, useState } from 'react';
import Image from 'next/image'
import { List, ListRowProps } from 'react-virtualized';
import AutoSizer from 'react-virtualized-auto-sizer';

import { Radio } from '@mui/material';

import SenatorListItem from '@/components/SenatorListItem'
import { useGameContext } from '@/contexts/GameContext'
import Senator from '@/classes/Senator';
import styles from "./SenatorList.module.css"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import PopularityIcon from "@/images/icons/popularity.svg"
import KnightsIcon from "@/images/icons/knights.svg"
import Faction from '@/classes/Faction';
import Collection from '@/classes/Collection';

interface SenatorsTabProps {
  selectable?: boolean
  height?: number
  margin?: number
  faction?: Faction
  radioSelectedSenator?: Senator | null
  setRadioSelectedSenator?: (senator: Senator | null) => void
}

// List of senators
const SenatorsTab = (props: SenatorsTabProps) => {
  const { allSenators } = useGameContext()

  const [filteredAndSortedSenators, setFilteredSenators] = useState<Collection<Senator>>(new Collection<Senator>())

  // Filter and sort the senator list
  useEffect(() => {
    let senators = allSenators.asArray
    if (props.faction) {
      senators = senators.filter(s => s.faction === props.faction?.id)
    }

    // Sort by name in alphabetical order
    senators = senators.sort((a, b) => a.name.localeCompare(b.name))

    setFilteredSenators(new Collection<Senator>(senators))
  }, [allSenators, props.faction])

  const handleRadioSelectSenator = (senator: Senator) => {
    if (props.setRadioSelectedSenator) props.setRadioSelectedSenator(senator)
  }

  // Function to render each row in the list
  const rowRenderer = ({ index, key, style }: ListRowProps) => {
    const senator: Senator = filteredAndSortedSenators.asArray[index]
  
    return (
      <div key={key} style={style} onClick={() => handleRadioSelectSenator(senator)}>
        <div className={ styles.listItem }>
          {props.setRadioSelectedSenator &&
            <div className={styles.radioContainer}>
              <Radio
                checked={props.radioSelectedSenator === senator}
                value={senator.name}
                inputProps={{ 'aria-label': senator.name}} />
            </div>
          }
          <SenatorListItem senator={senator} selectable={props.selectable} radioSelected={props.radioSelectedSenator === senator}/>
        </div>
      </div>
    )
  }

  const iconSize = 34

  return (
    <div className={styles.listContainer} style={{height: props.height, margin: props.margin ?? 0}}>
      <div className={`${styles.headers} ${props.setRadioSelectedSenator ? styles.radioHeaderMargin : ''}`}>
        <div><Image src={MilitaryIcon} height={iconSize} width={iconSize} alt="Military Icon" /></div>
        <div><Image src={OratoryIcon} height={iconSize} width={iconSize} alt="Oratory Icon" /></div>
        <div><Image src={LoyaltyIcon} height={iconSize} width={iconSize} alt="Loyalty Icon" /></div>
        <div><Image src={InfluenceIcon} height={iconSize} width={iconSize} alt="Influence Icon" /></div>
        <div><Image src={TalentsIcon} height={iconSize} width={iconSize} alt="Talents Icon" /></div>
        <div><Image src={PopularityIcon} height={iconSize} width={iconSize} alt="Popularity Icon" /></div>
        <div><Image src={KnightsIcon} height={iconSize} width={iconSize} alt="Knights Icon" /></div>
      </div>
      <div className={styles.list}>
        <AutoSizer>
          {({height, width}: {height: number, width: number}) => (
            <List
              width={width}
              height={height}
              rowCount={filteredAndSortedSenators.asArray.length}
              rowHeight={104}
              rowRenderer={rowRenderer}
            />
          )}
        </AutoSizer>
      </div>
    </div>
  )
}

export default SenatorsTab
