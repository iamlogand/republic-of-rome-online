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
const SenatorList = ({
  selectableSenators,
  selectableFactions,
  height,
  minHeight,
  faction,
  border,
  radioSelectedSenator,
  setRadioSelectedSenator,
  mainSenatorListGroupedState,
  mainSenatorListSortState,
  mainSenatorListFilterAliveState,
  mainSenatorListFilterDeadState,
}: SenatorListProps) => {
  const { allFactions, allSenators, selectedDetail } = useGameContext()

  // State for grouped, optionally passed in from the parent component
  const [localGrouped, setLocalGrouped] = useState<boolean>(false) // Whether to group senators by faction
  const grouped = mainSenatorListGroupedState
    ? mainSenatorListGroupedState[0]
    : localGrouped
  const setGrouped = mainSenatorListGroupedState
    ? mainSenatorListGroupedState[1]
    : setLocalGrouped

  // State for sort, optionally passed in from the parent component
  const [localSort, setLocalSort] = useState<string>("") // Attribute to sort by, prefixed with '-' for descending order
  const sort = mainSenatorListSortState
    ? mainSenatorListSortState[0]
    : localSort
  const setSort = mainSenatorListSortState
    ? mainSenatorListSortState[1]
    : setLocalSort

  // State for alive filter, optionally passed in from the parent component
  const [localFilterAlive, setLocalFilterAlive] = useState<boolean>(true)
  const filterAlive = mainSenatorListFilterAliveState
    ? mainSenatorListFilterAliveState[0]
    : localFilterAlive
  const setFilterAlive = mainSenatorListFilterAliveState
    ? mainSenatorListFilterAliveState[1]
    : setLocalFilterAlive

  // State for dead filter, optionally passed in from the parent component
  const [localFilterDead, setLocalFilterDead] = useState<boolean>(false)
  const filterDead = mainSenatorListFilterDeadState
    ? mainSenatorListFilterDeadState[0]
    : localFilterDead
  const setFilterDead = mainSenatorListFilterDeadState
    ? mainSenatorListFilterDeadState[1]
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
    if (faction) {
      senators = senators.filter((s) => s.faction === faction?.id)
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
    faction,
  ])

  // Auto scroll to the selected senator
  const [autoScrollTargetIndex, setAutoScrollTargetIndex] = useState<
    number | null
  >(null)
  const filteredSortedSenatorsRef = useRef<Senator[]>([])
  filteredSortedSenatorsRef.current = filteredSortedSenators.asArray

  useEffect(() => {
    if (selectedDetail?.type !== "Senator") return

    let selectedSenatorIndex = 0
    for (let i = 0; i < filteredSortedSenatorsRef.current.length; i++) {
      if (filteredSortedSenatorsRef.current[i].id === selectedDetail.id) {
        selectedSenatorIndex = i
        break
      }
    }
    console.log(selectedSenatorIndex)

    setAutoScrollTargetIndex(selectedSenatorIndex)
    setTimeout(() => setAutoScrollTargetIndex(null), 100)
  }, [selectedDetail])

  // Set stat widths
  const contentElementRef = useRef<HTMLDivElement>(null)
  const [statWidth, setStatWidth] = useState<number>(0)
  useEffect(() => {
    if (!contentElementRef.current) return
    const contentWidth = contentElementRef.current.clientWidth
    let width = Math.floor(contentWidth / 22)
    if (width < 26) width = 26
    if (width > 40) width = 40
    setStatWidth(width)
  }, [contentElementRef, statWidth, setStatWidth])

  // Handle clicking a senator when the list is radio selectable
  const handleRadioSelectSenator = (senator: Senator) => {
    if (setRadioSelectedSenator) setRadioSelectedSenator(senator)
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
          className="cursor-pointer border-none bg-transparent mt-[6px] p-0 flex flex-col justify-center items-center"
          style={{ width: statWidth + 6 }}
        >
          <Image
            src={header.icon}
            height={ICON_SIZE}
            width={ICON_SIZE}
            alt={`${titleCaseName} icon`}
            className="m-[-3px]"
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
        <div className="flex" role="row" aria-label={senator.displayName}>
          {setRadioSelectedSenator && (
            <div className="ml-2 flex items-center">
              <Radio
                checked={radioSelectedSenator === senator}
                value={senator.name}
                inputProps={{ "aria-label": senator.name }}
              />
            </div>
          )}
          <SenatorListItem
            senator={senator}
            selectableSenators={selectableSenators}
            selectableFactions={selectableFactions}
            radioSelected={radioSelectedSenator === senator}
            statWidth={statWidth}
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
      className="h-full box-border overflow-x-auto overflow-y-hidden flex flex-col rounded bg-white"
      style={{
        height: height,
        minHeight: minHeight ?? DEFAULT_MIN_HEIGHT,
      }}
    >
      <div
        className="h-full w-full flex flex-col"
        style={{ minWidth: setRadioSelectedSenator ? 446 : 406 }}
        ref={contentElementRef}
      >
        {statWidth > 0 && (
          <div
            className="rounded-t border border-solid border-stone-300 flex flex-wrap gap-y-2 user-select-none overflow-hidden pr-[2px]"
            style={faction && { backgroundColor: faction.getColor(50) }}
          >
            <div
              className={`h-[54px] box-border flex gap-[2px] items-start rounded ${
                setRadioSelectedSenator ? "box-border pl-[50px]" : ""
              }`}
              style={{ height: sort === "" ? 42 : 55 }}
            >
              <div className="h-[34px] min-w-[103px] mt-1 text-center flex justify-center items-center">
                {!faction && (
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
                    sx={{ "& .MuiFormControlLabel-label": { width: 60, fontSize: 13, lineHeight: 1.3 } }}
                  />
                )}
              </div>
              {headers.map((header) => getHeader(header))}
            </div>
            {!faction && (
              <div className="flex-1 flex items-start pl-2 pt-[6px]">
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
              <div className="px-4 py-2 flex flex-col">
                <h4>Senator Filters</h4>
                <FormControlLabel
                  control={<Checkbox checked={filterAlive} />}
                  label="Alive"
                  onChange={handleFilterAliveClick}
                  style={{ marginRight: 0 }}
                />
                <FormControlLabel
                  control={<Checkbox checked={filterDead} />}
                  label="Dead"
                  onChange={handleFilterDeadClick}
                  style={{ marginRight: 0 }}
                />
              </div>
            </Popover>
          </div>
        )}
        <div className="grow rounded-b border-t-0 border-b border-x border-solid border-stone-200">
          <div className="h-full box-border shadow-inner pb-px">
            <AutoSizer>
              {({ height, width }: { height: number; width: number }) => (
                <List
                  width={width}
                  height={height}
                  rowCount={filteredSortedSenators.allIds.length}
                  rowHeight={({ index }) =>
                    index === filteredSortedSenators.allIds.length - 1
                      ? 114
                      : 106
                  } // Last item has larger height to account for bottom margin
                  rowRenderer={rowRenderer}
                  scrollToIndex={autoScrollTargetIndex ?? undefined}
                />
              )}
            </AutoSizer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SenatorList
