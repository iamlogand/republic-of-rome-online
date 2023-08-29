import { useEffect, useState } from 'react';
import Image from 'next/image'
import { List, ListRowProps } from 'react-virtualized';
import AutoSizer from 'react-virtualized-auto-sizer';

import { Checkbox, FormControlLabel, Radio } from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronUp, faChevronDown } from '@fortawesome/free-solid-svg-icons'

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

type SortAttribute = "military" | "oratory" | "loyalty" | "influence" | "talents" | "popularity" | "knights"

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
  const { allFactions, allSenators } = useGameContext()

  const [sort, setSort] = useState<string>('')  // Attribute to sort by, prefixed with '-' for descending order
  const [grouped, setGrouped] = useState<boolean>(false)  // Whether to group senators by faction

  const [filteredSortedSenators, setFilteredSortedSenators] = useState<Collection<Senator>>(new Collection<Senator>())

  // Filter and sort the senator list
  useEffect(() => {
    let senators = allSenators.asArray
    if (props.faction) {
      senators = senators.filter(s => s.faction === props.faction?.id)
    }

    // Sort by name in alphabetical order as base/default order
    senators = senators.sort((a, b) => a.name.localeCompare(b.name))

    // Sort by the selected attribute
    if (sort !== '') {
      const isDescending = sort.startsWith('-');
      const attribute = sort.replace('-', '');
      senators = senators.sort((a, b) => {
        if (a[attribute as SortAttribute] > b[attribute as SortAttribute]) return isDescending ? -1 : 1;
        if (a[attribute as SortAttribute] < b[attribute as SortAttribute]) return isDescending ? 1 : -1;
        return 0;
      });
    }

    // Finally, sort by faction if grouped is true
    if (grouped) {
      senators = senators.sort((a, b) => {
        const factionA = allFactions.asArray.find(f => f.id === a.faction)
        const factionB = allFactions.asArray.find(f => f.id === b.faction)

        if (factionA === undefined && factionB === undefined) {
          return 0
        } else if (factionA === undefined) {
          return 1
        } else if (factionB === undefined) {
          return -1
        } else {
          return factionA.position - factionB.position
        }
      });
    }

    setFilteredSortedSenators(new Collection<Senator>(senators))
  }, [allSenators, sort, grouped, props.faction])

  const handleRadioSelectSenator = (senator: Senator) => {
    if (props.setRadioSelectedSenator) props.setRadioSelectedSenator(senator)
  }

  const handleSortClick = (attributeName: string) => {
    if (sort === attributeName) {
      setSort('')
    } else if (sort === `-${attributeName}`) {
      setSort(attributeName)
    } else {
      setSort(`-${attributeName}`)
    }
  }

  const handleGroupClick = () => {
    if (grouped === true) {
      setGrouped(false)
    } else {
      setGrouped(true)
    }
  }

  // Function to render each row in the list
  const rowRenderer = ({ index, key, style }: ListRowProps) => {
    const senator: Senator = filteredSortedSenators.asArray[index]
  
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
      <div className={`${styles.headers} ${props.setRadioSelectedSenator ? styles.radioHeaderMargin : ''}`}
        style={{height: sort === "" ? 42 : 55}}
      >
        <div className={styles.groupButton}>
          {!props.faction &&
            <FormControlLabel control={<Checkbox style={{ marginLeft: 0, marginRight: -8 }} checked={grouped} />}
              label="Group by Faction" onChange={handleGroupClick} style={{marginRight: 0}} />
          }
        </div>
        <div onClick={() => handleSortClick("military")}>
          <Image src={MilitaryIcon} height={iconSize} width={iconSize} alt="Military Icon" />
          {sort === "military" && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
          {sort === "-military" && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
        </div>
        <div onClick={() => handleSortClick("oratory")}>
          <Image src={OratoryIcon} height={iconSize} width={iconSize} alt="Oratory Icon" />
          {sort === "oratory" && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
          {sort === "-oratory" && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
        </div>
        <div onClick={() => handleSortClick("loyalty")}>
          <Image src={LoyaltyIcon} height={iconSize} width={iconSize} alt="Loyalty Icon" />
          {sort === "loyalty" && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
          {sort === "-loyalty" && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
        </div>
        <div onClick={() => handleSortClick("influence")}>
          <Image src={InfluenceIcon} height={iconSize} width={iconSize} alt="Influence Icon" />
          {sort === "influence" && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
          {sort === "-influence" && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
        </div>
        <div onClick={() => handleSortClick("talents")}>
          <Image src={TalentsIcon} height={iconSize} width={iconSize} alt="Talents Icon" />
          {sort === "talents" && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
          {sort === "-talents" && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
        </div>
        <div onClick={() => handleSortClick("popularity")}>
          <Image src={PopularityIcon} height={iconSize} width={iconSize} alt="Popularity Icon" />
          {sort === "popularity" && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
          {sort === "-popularity" && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
        </div>
        <div onClick={() => handleSortClick("knights")}>
          <Image src={KnightsIcon} height={iconSize} width={iconSize} alt="Knights Icon" />
          {sort === "knights" && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
          {sort === "-knights" && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
        </div>
      </div>
      <div className={styles.list}>
        <AutoSizer>
          {({height, width}: {height: number, width: number}) => (
            <List
              width={width}
              height={height}
              rowCount={filteredSortedSenators.asArray.length}
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
