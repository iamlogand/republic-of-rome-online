import React, { useRef } from "react"
import { useEffect, useState } from "react"
import Image from "next/image"
import { List, ListRowProps } from "react-virtualized"
import AutoSizer from "react-virtualized-auto-sizer"

import {
  Button,
  Checkbox,
  FormControlLabel,
  Popover,
  Radio,
  Tooltip,
} from "@mui/material"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import {
  faChevronUp,
  faChevronDown,
  faFilter,
} from "@fortawesome/free-solid-svg-icons"

import SenatorListItem from "@/components/SenatorListItem"
import { useGameContext } from "@/contexts/GameContext"
import Senator from "@/classes/Senator"
import styles from "./SenatorList.module.css"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import PopularityIcon from "@/images/icons/popularity.svg"
import KnightsIcon from "@/images/icons/knights.svg"
import VotesIcon from "@/images/icons/votes.svg"
import Faction from "@/classes/Faction"
import Collection from "@/classes/Collection"

type SortAttribute =
  | "military"
  | "oratory"
  | "loyalty"
  | "influence"
  | "talents"
  | "popularity"
  | "knights"
  | "votes"

const ICON_SIZE = 34

const DEFAULT_MIN_HEIGHT = 157

interface SenatorListProps {
  selectableSenators?: boolean
  selectableFactions?: boolean
  height?: number
  minHeight?: number
  faction?: Faction
  border?: boolean
  radioSelectedSenator?: Senator | null
  setRadioSelectedSenator?: (senator: Senator | null) => void
  mainSenatorListGroupedState?: [boolean, (grouped: boolean) => void]
  mainSenatorListSortState?: [string, (sort: string) => void]
  mainSenatorListFilterAliveState?: [boolean, (sort: boolean) => void]
  mainSenatorListFilterDeadState?: [boolean, (sort: boolean) => void]
}

// List of senators
const SenatorList = (props: SenatorListProps) => {
  const { allFactions, allSenators } = useGameContext()

  // State for grouped, optionally passed in from the parent component
  const [localGrouped, setLocalGrouped] = useState<boolean>(false) // Whether to group senators by faction
  const grouped = props.mainSenatorListGroupedState
    ? props.mainSenatorListGroupedState[0]
    : localGrouped
  const setGrouped = props.mainSenatorListGroupedState
    ? props.mainSenatorListGroupedState[1]
    : setLocalGrouped

  // State for sort, optionally passed in from the parent component
  const [localSort, setLocalSort] = useState<string>("") // Attribute to sort by, prefixed with '-' for descending order
  const sort = props.mainSenatorListSortState
    ? props.mainSenatorListSortState[0]
    : localSort
  const setSort = props.mainSenatorListSortState
    ? props.mainSenatorListSortState[1]
    : setLocalSort

  // State for alive filter, optionally passed in from the parent component
  const [localFilterAlive, setLocalFilterAlive] = useState<boolean>(true)
  const filterAlive = props.mainSenatorListFilterAliveState
    ? props.mainSenatorListFilterAliveState[0]
    : localFilterAlive
  const setFilterAlive = props.mainSenatorListFilterAliveState
    ? props.mainSenatorListFilterAliveState[1]
    : setLocalFilterAlive

  // State for dead filter, optionally passed in from the parent component
  const [localFilterDead, setLocalFilterDead] = useState<boolean>(false)
  const filterDead = props.mainSenatorListFilterDeadState
    ? props.mainSenatorListFilterDeadState[0]
    : localFilterDead
  const setFilterDead = props.mainSenatorListFilterDeadState
    ? props.mainSenatorListFilterDeadState[1]
    : setLocalFilterDead

  const [anchorElement, setAnchorElement] =
    React.useState<HTMLButtonElement | null>(null)

  // State for the filtered and sorted senators
  const [filteredSortedSenators, setFilteredSortedSenators] = useState<
    Collection<Senator>
  >(new Collection<Senator>())

  // Filter, group and sort the senators
  useEffect(() => {
    let senators = allSenators.asArray

    // If showing only one faction, filter to only that faction
    if (props.faction) {
      senators = senators.filter((s) => s.faction === props.faction?.id)
    }

    // Apply alive and dead filters
    senators = senators.filter(
      (s) => (filterAlive && s.alive) || (filterDead && !s.alive)
    )

    // Sort by generation in ascending order as base/default order
    senators = senators.sort((a, b) => a.generation - b.generation)

    // Sort by name in alphabetical order
    senators = senators.sort((a, b) => a.name.localeCompare(b.name))

    // Sort by the selected attribute
    if (sort !== "") {
      const isDescending = sort.startsWith("-")
      const attribute = sort.replace("-", "")
      senators = senators.sort((a, b) => {
        if (a[attribute as SortAttribute] > b[attribute as SortAttribute])
          return isDescending ? -1 : 1
        if (a[attribute as SortAttribute] < b[attribute as SortAttribute])
          return isDescending ? 1 : -1
        return 0
      })
    }

    // Finally, sort by faction if grouped is true
    if (grouped) {
      senators = senators.sort((a, b) => {
        const factionARank = allFactions.byId[a.faction]?.rank ?? null
        const factionBRank = allFactions.byId[b.faction]?.rank ?? null

        if (factionARank === null && factionBRank === null) {
          return 0
        } else if (factionARank === null) {
          return 1
        } else if (factionBRank === null) {
          return -1
        } else {
          return factionARank - factionBRank
        }
      })
    }

    setFilteredSortedSenators(new Collection<Senator>(senators))
  }, [
    allSenators,
    sort,
    grouped,
    allFactions,
    filterAlive,
    filterDead,
    props.faction,
  ])

  // Handle clicking a senator when the list is radio selectable
  const handleRadioSelectSenator = (senator: Senator) => {
    if (props.setRadioSelectedSenator) props.setRadioSelectedSenator(senator)
  }

  // Handle clicking a header to sort by that attribute
  const handleSortClick = (attributeName: string) => {
    if (sort === attributeName) {
      setSort("")
    } else if (sort === `-${attributeName}`) {
      setSort(attributeName)
    } else {
      setSort(`-${attributeName}`)
    }
  }

  // Handle clicking the group button to toggle grouping
  const handleGroupClick = () =>
    grouped ? setGrouped(false) : setGrouped(true)

  // Handle clicking the alive filter button to toggle showing alive senators
  const handleFilterAliveClick = () =>
    filterAlive ? setFilterAlive(false) : setFilterAlive(true)

  // Handle clicking the dead filter button to toggle showing dead senators
  const handleFilterDeadClick = () =>
    filterDead ? setFilterDead(false) : setFilterDead(true)

  // Handle clicking the filters button to open the filters popover
  const handleOpenFiltersClick = (event: React.MouseEvent<HTMLButtonElement>) =>
    setAnchorElement(event.currentTarget)

  // Handle closure of the filters popover
  const handleCloseFilters = () => setAnchorElement(null)

  // Headers for the list
  const headers = [
    { name: "military", icon: MilitaryIcon },
    { name: "oratory", icon: OratoryIcon },
    { name: "loyalty", icon: LoyaltyIcon },
    { name: "influence", icon: InfluenceIcon },
    { name: "talents", icon: TalentsIcon },
    { name: "popularity", icon: PopularityIcon },
    { name: "knights", icon: KnightsIcon },
    { name: "votes", icon: VotesIcon },
  ]

  // Get JSX for each header
  const getHeader = (header: { name: string; icon: string }) => {
    const titleCaseName = header.name[0].toUpperCase() + header.name.slice(1)
    return (
      <Tooltip
        key={header.name}
        title={titleCaseName}
        enterDelay={500}
        placement="top"
        arrow
      >
        <button
          onClick={() => handleSortClick(header.name)}
          className={styles.header}
        >
          <Image
            src={header.icon}
            height={ICON_SIZE}
            width={ICON_SIZE}
            alt={`${titleCaseName} icon`}
          />
          {sort === header.name && (
            <FontAwesomeIcon icon={faChevronUp} fontSize={18} />
          )}
          {sort === `-${header.name}` && (
            <FontAwesomeIcon icon={faChevronDown} fontSize={18} />
          )}
        </button>
      </Tooltip>
    )
  }

  // Get JSX for each row in the list
  const rowRenderer = ({ index, key, style }: ListRowProps) => {
    const senator: Senator = filteredSortedSenators.asArray[index]

    return (
      <div
        key={key}
        style={style}
        onClick={() => handleRadioSelectSenator(senator)}
      >
        <div
          className={styles.listItem}
          role="row"
          aria-label={senator.displayName}
        >
          {props.setRadioSelectedSenator && (
            <div className={styles.radioContainer}>
              <Radio
                checked={props.radioSelectedSenator === senator}
                value={senator.name}
                inputProps={{ "aria-label": senator.name }}
              />
            </div>
          )}
          <SenatorListItem
            senator={senator}
            selectableSenators={props.selectableSenators}
            selectableFactions={props.selectableFactions}
            radioSelected={props.radioSelectedSenator === senator}
          />
        </div>
      </div>
    )
  }

  // Filter menu
  const filtersOpen = Boolean(anchorElement)
  const filtersId = filtersOpen ? "filter-menu" : undefined

  return (
    <div
      className={`${styles.listContainer} ${props.border ? styles.border : ""}`}
      style={{
        height: props.height,
        minHeight: props.minHeight ?? DEFAULT_MIN_HEIGHT,
      }}
    >
      <div
        className={styles.content}
        style={{ minWidth: props.setRadioSelectedSenator ? 446 : 406 }}
      >
        <div className={styles.headersAndFilters} style={props.faction && {backgroundColor: props.faction.getColor(50)}}>
          <div
            className={`${styles.headers} ${
              props.setRadioSelectedSenator ? styles.radioHeaderMargin : ""
            }`}
            style={{ height: sort === "" ? 42 : 55 }}
          >
            <div className={styles.groupButton}>
              {!props.faction && (
                <FormControlLabel
                  control={
                    <Checkbox
                      style={{ marginLeft: 0, marginRight: -8 }}
                      checked={grouped}
                    />
                  }
                  label="Group by Faction"
                  onChange={handleGroupClick}
                  style={{ marginRight: 0 }}
                  className={styles.header}
                />
              )}
            </div>
            {headers.map((header) => getHeader(header))}
          </div>
          {!props.faction && (
            <div className={styles.openFiltersContainer}>
              <Button
                aria-describedby={filtersId}
                onClick={handleOpenFiltersClick}
                size="small"
                aria-label="Filters"
              >
                <FontAwesomeIcon
                  icon={faFilter}
                  fontSize={18}
                  style={{ marginRight: 8 }}
                />{" "}
                Filters
              </Button>
            </div>
          )}
          <Popover
            id={filtersId}
            open={filtersOpen}
            anchorEl={anchorElement}
            onClose={handleCloseFilters}
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "center",
            }}
            transformOrigin={{
              vertical: "top",
              horizontal: "center",
            }}
          >
            <div className={styles.filters}>
              <h4>Senator Filters</h4>
              <FormControlLabel
                control={<Checkbox checked={filterAlive} />}
                label="Alive"
                onChange={handleFilterAliveClick}
                style={{ marginRight: 0 }}
                className={styles.header}
              />
              <FormControlLabel
                control={<Checkbox checked={filterDead} />}
                label="Dead"
                onChange={handleFilterDeadClick}
                style={{ marginRight: 0 }}
                className={styles.header}
              />
            </div>
          </Popover>
        </div>
        <div className={`${styles.list} shadow-inner`}>
          <AutoSizer>
            {({ height, width }: { height: number; width: number }) => (
              <List
                width={width}
                height={height}
                rowCount={filteredSortedSenators.allIds.length}
                rowHeight={({ index }) =>
                  index === filteredSortedSenators.allIds.length - 1 ? 114 : 106
                } // Last item has larger height to account for bottom margin
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
