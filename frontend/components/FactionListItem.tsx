import Image from "next/image"
import Tooltip from "@mui/material/Tooltip"

import SenatorPortrait from "@/components/SenatorPortrait"
import Collection from "@/classes/Collection"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import FactionLink from "@/components/FactionLink"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import VotesIcon from "@/images/icons/votes.svg"

type Attribute = {
  name: "senators" | "influence" | "votes" | "talents"
  value: Number
  image: string
  sum?: boolean
}

interface FactionListItemProps {
  faction: Faction
}

// Item in the faction list
const FactionListItem = (props: FactionListItemProps) => {
  const { allPlayers, allSenators } = useGameContext()

  // Get faction-specific data
  const player = allPlayers.byId[props.faction.player] ?? null
  const senators = new Collection<Senator>(
    allSenators.asArray
      .filter((s) => s.alive) // Filter by alive
      .filter((s) => s.faction === props.faction.id) // Filter by faction
      .sort((a, b) => a.generation - b.generation) // Sort by generation
      .sort((a, b) => a.name.localeCompare(b.name)) ?? [] // Sort by name
  )
  const totalInfluence = senators.asArray.reduce(
    (total, senator) => total + senator.influence,
    0
  )
  const totalTalents = senators.asArray.reduce(
    (total, senator) => total + senator.talents,
    0
  )
  const totalVotes = senators.asArray.reduce(
    (total, senator) => total + senator.votes,
    0
  )

  // Attribute data
  const attributeItems: Attribute[] = [
    {
      name: "influence",
      value: totalInfluence,
      image: InfluenceIcon,
    },
    { name: "talents", value: totalTalents, image: TalentsIcon },
    { name: "votes", value: totalVotes, image: VotesIcon },
  ]

  // Get attribute items
  const getAttributeItem = (item: Attribute) => {
    const titleCaseName =
      "Total " + item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <Tooltip key={item.name} title={titleCaseName} enterDelay={500} arrow>
        <div className="w-[64px] grid grid-cols-[30px_30px] items-center justify-center bg-white shadow-[0px_0px_2px_2px_white] rounded">
          <Image
            src={item.image}
            height={28}
            width={28}
            alt={`${titleCaseName} icon`}
          />
          <div className="w-8 text-center">{item.value.toString()}</div>
        </div>
      </Tooltip>
    )
  }

  if (!player?.user || senators.allIds.length === 0) return null

  return (
    <div
      className="flex-1 box-border p-2 rounded flex flex-col gap-2 border border-solid"
      style={{
        backgroundColor: props.faction.getColor(100),
        borderColor: props.faction.getColor(300),
      }}
    >
      <p>
        <b>
          <FactionLink faction={props.faction} includeIcon />
        </b>{" "}
        of {player.user.username}
      </p>
      <div className="p-[2px] flex flex-wrap gap-3 select-none">
        {attributeItems.map((item) => getAttributeItem(item))}
      </div>
      <div className="flex flex-wrap gap-2">
        {senators.asArray.map((senator: Senator) => (
          <SenatorPortrait
            key={senator.id}
            senator={senator}
            size={80}
            selectable
            nameTooltip
          />
        ))}
      </div>
    </div>
  )
}

export default FactionListItem
