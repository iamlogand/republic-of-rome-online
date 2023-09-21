
import React, { useRef } from 'react'
import { useEffect, useState } from 'react'
import Image from 'next/image'
import { List, ListRowProps } from 'react-virtualized'
import AutoSizer from 'react-virtualized-auto-sizer'

import { Button, Checkbox, FormControlLabel, Popover, Radio } from '@mui/material'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faChevronUp, faChevronDown, faFilter } from '@fortawesome/free-solid-svg-icons'

import SenatorListItem from '@/components/SenatorListItem'
import { useGameContext } from '@/contexts/GameContext'
import Senator from '@/classes/Senator'
import styles from "./SenatorList.module.css"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import PopularityIcon from "@/images/icons/popularity.svg"
import KnightsIcon from "@/images/icons/knights.svg"
import VotesIcon from "@/images/icons/votes.svg"
import Faction from '@/classes/Faction'
import Collection from '@/classes/Collection'

type SortAttribute = "military" | "oratory" | "loyalty" | "influence" | "talents" | "popularity" | "knights" | "votes"

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

  const [filterAlive, setFilterAlive] = useState<boolean>(true)
  const [filterDead, setFilterDead] = useState<boolean>(false)
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null)

  const [filteredSortedSenators, setFilteredSortedSenators] = useState<Collection<Senator>>(new Collection<Senator>())

  // Filter and sort the senator list
  useEffect(() => {
    let senators = allSenators.asArray
    if (props.faction) {
      senators = senators.filter(s => s.faction === props.faction?.id)
    }

    // Apply filters
    senators = senators.filter(s => (filterAlive && s.alive) || (filterDead && !s.alive))

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

        if (factionA === null && factionB === null) {
          return 0
        } else if (factionA === null) {
          return 1
        } else if (factionB === null) {
          return -1
        } else {
          return factionA.position - factionB.position
        }
      });
    }

    setFilteredSortedSenators(new Collection<Senator>(senators))
  }, [allSenators, sort, grouped, allFactions, filterAlive, filterDead, props.faction])

  const handleRadioSelectSenator = (senator: Senator) => {
    if (props.setRadioSelectedSenator) props.setRadioSelectedSenator(senator)
  }

  // Grouping, sorting, and filtering functions

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

  const handleFilterAliveClick = () => {
    if (filterAlive === true) {
      setFilterAlive(false)
    } else {
      setFilterAlive(true)
    }
  }

  const handleFilterDeadClick = () => {
    if (filterDead === true) {
      setFilterDead(false)
    } else {
      setFilterDead(true)
    }
  }

  const handleOpenFiltersClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleCloseFiltersClick = () => {
    setAnchorEl(null)
  }

  // Function to render each row in the list
  const rowRenderer = ({ index, key, style }: ListRowProps) => {
    const senator: Senator = filteredSortedSenators.asArray[index]
  
    return (
      <div key={key} style={style} onClick={() => handleRadioSelectSenator(senator)}>
        <div className={ styles.listItem } role="row" aria-label={senator.name}>
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
    { sort: "votes", icon: VotesIcon, alt: "Votes Icon" },
  ];

  const filtersOpen = Boolean(anchorEl);
  const filtersId = filtersOpen ? 'filter-menu' : undefined;

  return (
    <div className={styles.listContainer}
      style={{height: props.height, margin: props.margin ?? 0, minHeight: props.minHeight ?? DEFAULT_MIN_HEIGHT }}
    >
      <div className={styles.content} style={{ minWidth: props.setRadioSelectedSenator ? 446 : 406 }}>
        <div className={styles.headersAndFilters}>
          <div className={`${styles.headers} ${props.setRadioSelectedSenator ? styles.radioHeaderMargin : ''}`} style={{ height: sort === "" ? 42 : 55 }}>
            <div className={styles.groupButton}>
              {!props.faction &&
                <FormControlLabel control={<Checkbox style={{ marginLeft: 0, marginRight: -8 }} checked={grouped} />}
                  label="Group by Faction" onChange={handleGroupClick}
                  style={{marginRight: 0}} className={styles.header}
                />
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
          {!props.faction && <div className={styles.openFiltersContainer}>
            <Button aria-describedby={filtersId} onClick={handleOpenFiltersClick} size="small" aria-label="Filters">
              <FontAwesomeIcon icon={faFilter} fontSize={18} style={{ marginRight: 8 }}/> Filters
            </Button>
          </div>}
          <Popover id={filtersId} open={filtersOpen} anchorEl={anchorEl}
            onClose={handleCloseFiltersClick}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'center',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'center',
            }}
          >
            <div className={styles.filters}>
              <h4>Senator Filters</h4>
              <FormControlLabel control={<Checkbox checked={filterAlive} />}
                label="Alive" onChange={handleFilterAliveClick}
                style={{marginRight: 0}} className={styles.header}
              />
              <FormControlLabel control={<Checkbox checked={filterDead} />}
                label="Dead" onChange={handleFilterDeadClick}
                style={{marginRight: 0}} className={styles.header}
              />
            </div>
          </Popover>
        </div>
        <div className={styles.list}>
          <AutoSizer>
            {({height, width}: {height: number, width: number}) => (
              <List
                width={width}
                height={height}
                rowCount={filteredSortedSenators.allIds.length}
                rowHeight={({ index }) => index === filteredSortedSenators.allIds.length - 1 ? 112 : 104}  // Last item has larger height to account for bottom margin
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
