import { Tooltip } from "@mui/material"

import SenatorPortrait from "@/components/SenatorPortrait"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import skillsJSON from "@/data/skills.json"
import SenatorLink from "@/components/SenatorLink"
import FactionLink from "@/components/FactionLink"
import SenatorFactList from "@/components/SenatorFactList"
import { useAuthContext } from "@/contexts/AuthContext"

type FixedAttribute = "military" | "oratory" | "loyalty"

type Attribute = {
  name: FixedAttribute | string
  value: number
  fixed?: boolean
}

interface SenatorListItemProps {
  senator: Senator
  selectable?: boolean
  radioSelected?: boolean
  statWidth?: number
}

// Item in the senator list
const SenatorListItem = ({ senator, ...props }: SenatorListItemProps) => {
  const { darkMode } = useAuthContext()
  const { allFactions, allTitles, selectedDetail } = useGameContext()

  // Get senator-specific data
  const faction: Faction | null = senator.faction
    ? allFactions.byId[senator.faction] ?? null
    : null
  const factionLeader: boolean = allTitles.asArray.some(
    (o) => o.senator === senator.id && o.name == "Faction Leader"
  )

  // Attribute data
  const attributes: Attribute[] = [
    { name: "military", value: senator.military, fixed: true },
    { name: "oratory", value: senator.oratory, fixed: true },
    { name: "loyalty", value: senator.loyalty, fixed: true },
    { name: "influence", value: senator.influence },
    { name: "talents", value: senator.talents },
    { name: "popularity", value: senator.popularity },
    { name: "knights", value: senator.knights },
    { name: "votes", value: senator.votes },
  ]

  // Get JSX for an attribute item
  const getAttributeItem = (item: Attribute, index: number) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    let style: React.CSSProperties = {}
    if (item.fixed) {
      style.color = "white"
      style.backgroundColor =
        skillsJSON.colors.number[item.name as FixedAttribute]
      style.boxShadow = `0px 0px 2px 2px ${
        skillsJSON.colors.number[item.name as FixedAttribute]
      }`
    } else {
      const attributeBgColor = darkMode
        ? index % 2 == 0
          ? "#57534e"
          : "#78716c"
        : index % 2 == 0
        ? "#e7e5e4"
        : "white"
      style.backgroundColor = attributeBgColor
      style.boxShadow = `0px 0px 2px 2px ${attributeBgColor}`
    }
    style.width = props.statWidth ?? "26px"

    return (
      <Tooltip key={item.name} title={titleCaseName} arrow>
        <div
          aria-label={titleCaseName}
          className="text-center m-[3px] leading-5 select-none font-semibold rounded-sm"
          style={style}
        >
          {item.value}
        </div>
      </Tooltip>
    )
  }

  // Get style for selected item
  const getSelectedStyle = () => {
    if (darkMode) {
      return {
        boxShadow: "inset 0 0 0 1px hsl(316, 80%, 85%)", // tyrian-200
        borderColor: "hsl(316, 80%, 85%)", // tyrian-200
        backgroundColor: "hsla(331, 62%, 30%, 0.2)", // tyrian-700 with 20% opacity
      }
    } else {
      return {
        boxShadow: "inset 0 0 0 1px hsl(325, 40%, 50%)", // tyrian-500
        borderColor: "hsl(325, 40%, 50%)", // tyrian-500
        backgroundColor: "hsl(310, 100%, 97%)", // tyrian-50
      }
    }
  }

  return (
    <div
      key={senator.id}
      className="flex-1 h-[98px] mt-2 mx-2 mb-0 box-border bg-stone-100 dark:bg-stone-700 rounded flex gap-2 border border-solid border-stone-300 dark:border-stone-800"
      style={
        props.radioSelected ||
        (selectedDetail?.type === "Senator" &&
          selectedDetail?.id === senator.id &&
          props.selectable)
          ? getSelectedStyle()
          : {}
      }
      aria-selected={props.radioSelected}
    >
      <div
        className={`p-2 ${
          props.statWidth && props.statWidth > 30 ? "pr-2" : "pr-0"
        }`}
      >
        <SenatorPortrait
          senator={senator}
          size={80}
          selectable={props.selectable}
          blurryPlaceholder
        />
      </div>
      <div className="w-full flex flex-col justify-between">
        <div
          className={`h-full flex ${
            props.statWidth && props.statWidth > 30 ? "gap-8" : "gap-4"
          }`}
        >
          <div
            className="flex flex-col py-[7px] justify-between"
            style={{ whiteSpace: "nowrap" }}
          >
            <p>
              <b>
                {props.selectable ? (
                  <SenatorLink senator={senator} />
                ) : (
                  <span>{senator.displayName}</span>
                )}
              </b>
            </p>
            <p className="">
              {faction && senator.alive ? (
                props.selectable ? (
                  <span>
                    <FactionLink faction={faction} includeIcon />{" "}
                    {factionLeader && "Leader"}
                  </span>
                ) : (
                  factionLeader && <span>Faction Leader</span>
                )
              ) : senator.alive ? (
                "Unaligned"
              ) : (
                "Dead"
              )}
            </p>
          </div>
          <div
            className={`w-full max-h-14 mr-px mt-px ${
              props.statWidth && props.statWidth > 30 ? "pl-4" : "pl-2"
            } py-[6px] pr-1 box-border flex justify-end items-center bg-[#ffffff99] dark:bg-[#ffffff0c] rounded-tr rounded-bl-lg text-end`}
          >
            <div
              className={`max-h-full overflow-auto ${
                props.statWidth && props.statWidth > 30 ? "pr-3" : "pr-1"
              }`}
            >
              <SenatorFactList
                senator={senator}
                selectable={props.selectable}
              />
            </div>
          </div>
        </div>
        <div className="flex pb-2">
          <div className="flex gap-[2px]">
            {attributes.map((item, index) => getAttributeItem(item, index))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SenatorListItem
