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

const DEFAULT_MIN_HEIGHT = 260

interface SenatorListProps {
  selectableSenators?: boolean
  selectableFactions?: boolean
  height?: number
  minHeight?: number
  margin?: number
  faction?: Faction
  radioSelectedSenator?: Senator | null
  setRadioSelectedSenator?: (senator: Senator | null) => void
  mainSenatorListSortState?: [string, (sort: string) => void]
  mainSenatorListGroupedState?: [boolean, (grouped: boolean) => void]
}

// List of senators
const SenatorList = (props: SenatorListProps) => {
  const { allFactions, allSenators } = useGameContext()

  // State for sorting and grouping. Optionally passed in from parent component
  const [localSort, setLocalSort] = useState<string>('')  // Attribute to sort by, prefixed with '-' for descending order
  const [localGrouped, setLocalGrouped] = useState<boolean>(false)  // Whether to group senators by faction
  const sort = props.mainSenatorListSortState ? props.mainSenatorListSortState[0] : localSort
  const setSort = props.mainSenatorListSortState ? props.mainSenatorListSortState[1] : setLocalSort
  const grouped = props.mainSenatorListGroupedState ? props.mainSenatorListGroupedState[0] : localGrouped
  const setGrouped = props.mainSenatorListGroupedState ? props.mainSenatorListGroupedState[1] : setLocalGrouped

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
        const factionA = allFactions.byId[a.faction] ?? null
        const factionB = allFactions.byId[b.faction] ?? null

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
  }, [allSenators, sort, grouped, allFactions, props.faction])

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
          <SenatorListItem senator={senator} selectableSenators={props.selectableSenators} selectableFactions={props.selectableFactions} radioSelected={props.radioSelectedSenator === senator}/>
        </div>
      </div>
    )
  }

  const iconSize = 34

  const headers = [
    { sort: "military", icon: MilitaryIcon, alt: "Military Icon" },
    { sort: "oratory", icon: OratoryIcon, alt: "Oratory Icon" },
    { sort: "loyalty", icon: LoyaltyIcon, alt: "Loyalty Icon" },
    { sort: "influence", icon: InfluenceIcon, alt: "Influence Icon" },
    { sort: "talents", icon: TalentsIcon, alt: "Talents Icon" },
    { sort: "popularity", icon: PopularityIcon, alt: "Popularity Icon" },
    { sort: "knights", icon: KnightsIcon, alt: "Knights Icon" },
  ];

  return (
    <div className={styles.listContainer}
      style={{height: props.height, margin: props.margin ?? 0, minHeight: props.minHeight ?? DEFAULT_MIN_HEIGHT }}
    >
      <div className={styles.content} style={{ minWidth: props.setRadioSelectedSenator ? 390 : 350 }}>
        <div className={`${styles.headers} ${props.setRadioSelectedSenator ? styles.radioHeaderMargin : ''}`}
          style={{height: sort === "" ? 42 : 55}}
        >
          <div className={styles.groupButton}>
            {!props.faction &&
              <FormControlLabel control={<Checkbox style={{ marginLeft: 0, marginRight: -8 }} checked={grouped} />}
                label="Group by Faction" onChange={handleGroupClick}
                style={{marginRight: 0}} className={styles.header}/>
            }
          </div>
          {headers.map(header => (
            <button onClick={() => handleSortClick(header.sort)} className={styles.header} key={header.sort}>
              <Image src={header.icon} height={iconSize} width={iconSize} alt={header.alt} />
              {sort === header.sort && <FontAwesomeIcon icon={faChevronUp} fontSize={18} />}
              {sort === `-${header.sort}` && <FontAwesomeIcon icon={faChevronDown} fontSize={18} />}
            </button>
          ))}
        </div>
        <div className={styles.list}>
          <AutoSizer>
            {({height, width}: {height: number, width: number}) => (
              <List
                width={width}
                height={height}
                rowCount={filteredSortedSenators.allIds.length}
                rowHeight={104}
                rowRenderer={rowRenderer}
              />
            )}
          </AutoSizer>
        </div>
      </div>
    </div>
  )
}

export default SenatorList
