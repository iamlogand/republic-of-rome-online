import { Box, Tab, Tabs } from "@mui/material"
import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Faction.module.css"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import SenatorList from "@/components/SenatorList"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import VotesIcon from "@/images/icons/votes.svg"
import SenatorsIcon from "@/images/icons/senators.svg"
import AttributeGrid, { Attribute } from "@/components/AttributeGrid"
import SenatorPortrait from "@/components/SenatorPortrait"

// Detail section content for a faction
const FactionDetails = () => {
  const {
    allPlayers,
    allFactions,
    allSenators,
    selectedDetail,
    factionDetailTab,
    setFactionDetailTab,
  } = useGameContext()

  // Get faction-specific data
  let senators: Collection<Senator> = new Collection<Senator>([])
  if (selectedDetail && selectedDetail.type == "Faction") {
    senators = new Collection<Senator>(
      allSenators.asArray.filter((s) => s.faction === selectedDetail.id)
    )
  }
  const faction: Faction | null = selectedDetail?.id
    ? allFactions.byId[selectedDetail.id] ?? null
    : null
  const player: Player | null = faction?.player
    ? allPlayers.byId[faction.player] ?? null
    : null

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

  // Change selected tab
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setFactionDetailTab(newValue)
  }

  // Attribute data
  const attributes: Attribute[] = [
    { name: "Senators", value: senators.allIds.length, icon: SenatorsIcon },
    {
      name: "Total Influence",
      value: totalInfluence,
      icon: InfluenceIcon,
    },
    { name: "Total Talents", value: totalTalents, icon: TalentsIcon },
    { name: "Total Votes", value: totalVotes, icon: VotesIcon },
  ]

  // If there is no faction selected, render nothing
  if (!faction) return null

  return (
    <div className={styles.factionDetails}>
      <div className={styles.primaryArea}>
        <div className={styles.titleArea}>
          <span className={styles.factionIcon}>
            <FactionIcon faction={faction} size={26} />
          </span>
          <h4>
            <b>{faction.getName()} Faction</b> of{" "}
            {player ? player.user?.username : "unknown"}
          </h4>
        </div>
      </div>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={factionDetailTab}
          onChange={handleTabChange}
          className="px-2"
        >
          <Tab label="Overview" />
          <Tab label="Senators" />
        </Tabs>
      </Box>
      <div className="grow overflow-y-auto mx-2">
        {factionDetailTab === 0 && (
          <div className="flex flex-col gap-2">
            <div className="p-2 flex flex-col gap-2 bg-[var(--background-color)] rounded">
              <AttributeGrid attributes={attributes} />
            </div>
            <div className="flex flex-wrap gap-2">
              {senators.asArray.map((senator: Senator) => (
                <SenatorPortrait
                  key={senator.id}
                  senator={senator}
                  size={90}
                  selectable
                  nameTooltip
                />
              ))}
            </div>
          </div>
        )}
        {factionDetailTab === 1 && (
          <SenatorList faction={faction} selectableSenators />
        )}
      </div>
    </div>
  )
}

export default FactionDetails
