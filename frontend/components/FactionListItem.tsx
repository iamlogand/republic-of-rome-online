import SenatorPortrait from "@/components/SenatorPortrait"
import Collection from "@/classes/Collection"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import FactionLink from "@/components/FactionLink"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import VotesIcon from "@/images/icons/votes.svg"
import SecretsIcon from "@/images/icons/secrets.svg"
import AttributeFlex, { Attribute } from "@/components/AttributeFlex"
import { useCookieContext } from "@/contexts/CookieContext"

interface FactionListItemProps {
  faction: Faction
}

// Item in the faction list
const FactionListItem = (props: FactionListItemProps) => {
  const { darkMode } = useCookieContext()
  const { allPlayers, allSenators, allSecrets } = useGameContext()

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
    (total, senator) => total + senator.personalTreasury,
    0
  )
  const totalVotes = senators.asArray.reduce(
    (total, senator) => total + senator.votes,
    0
  )
  const secrets = allSecrets.asArray.filter(
    (s) => s.faction === props.faction?.id
  )

  // Attribute data
  const attributeItems: Attribute[] = [
    {
      name: "Combined Influence",
      value: totalInfluence,
      icon: InfluenceIcon,
    },
    {
      name: "Combined Personal Treasuries",
      value: totalTalents,
      icon: TalentsIcon,
    },
    { name: "Combined Votes", value: totalVotes, icon: VotesIcon },
    { name: "Secrets", value: secrets.length, icon: SecretsIcon },
  ]

  if (!player?.user || senators.allIds.length === 0) return null

  return (
    <div
      className="flex-1 box-border p-2 rounded flex flex-col gap-2 border border-solid"
      style={{
        backgroundColor: darkMode
          ? props.faction.getColor(900)
          : props.faction.getColor(100),
        border: `solid 1px ${
          darkMode ? props.faction.getColor(950) : props.faction.getColor(300)
        }`,
      }}
    >
      <p>
        <b>
          <FactionLink faction={props.faction} includeIcon  hiddenUnderline/>
        </b>
      </p>
      <AttributeFlex attributes={attributeItems} />
      <div className="flex flex-wrap gap-2">
        {senators.asArray.map((senator: Senator) => (
          <SenatorPortrait
            key={senator.id}
            senator={senator}
            size={80}
            selectable
            summary
            blurryPlaceholder
          />
        ))}
      </div>
    </div>
  )
}

export default FactionListItem
