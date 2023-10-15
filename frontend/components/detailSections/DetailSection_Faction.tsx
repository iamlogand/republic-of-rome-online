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
import Title from "@/classes/Title"
import SenatorLink from "@/components/SenatorLink"
import TermLink from "../TermLink"

// Detail section content for a faction
const FactionDetails = () => {
  const {
    allPlayers,
    allFactions,
    allSenators,
    allTitles,
    selectedDetail,
    factionDetailTab,
    setFactionDetailTab,
  } = useGameContext()

  // Get faction-specific data
  let senators: Collection<Senator> = new Collection<Senator>([])
  if (selectedDetail && selectedDetail.type == "Faction") {
    senators = new Collection<Senator>(
      allSenators.asArray.filter((s) => s.faction === selectedDetail.id && s.alive === true)
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

  // Get faction leader
  const factionLeaderTitle: Title | null =
    allTitles.asArray.find(
      (t) =>
        t.end_step === null &&
        t.name === "Faction Leader" &&
        senators.allIds.includes(t.senator)
    ) ?? null
  const factionLeader: Senator | null =
    senators.asArray.find((s) => s.id === factionLeaderTitle?.senator) ?? null

  // Get the HRAO if they're in this faction
  const hraoSenator: Senator | null =
    allSenators.asArray.find(
      (s) => s.rank === 0 && s.faction === faction?.id
    ) ?? null

  // Get major offices
  const majorOffices: Title[] =
    allTitles.asArray.filter(
      (t) =>
        t.end_step === null &&
        t.major_office === true &&
        senators.allIds.includes(t.senator)
    ) ?? null

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

  // GetJSX for the faction description
  const getFactionDescription = () => {
    const significantSenatorCount = hraoSenator ? 1 : 0 + majorOffices.length
    return (
      <p>
        The {faction.getName()} Faction
        {factionLeader && (
          <span>
            , led by <SenatorLink senator={factionLeader} />,
          </span>
        )}{" "}
        has {senators.allIds.length} members
        {hraoSenator && (
          <span>
            , including the{" "}
            <TermLink
              name="HRAO"
              tooltipTitle="Highest Ranking Available Official"
            />
          </span>
        )}
        {majorOffices.length > 0 &&
          majorOffices.map((office, index) => {
            const senator = senators.asArray.find((s) => s.id == office.senator)
            if (!senator) return null
            return (
              <span>
                {index === significantSenatorCount - 1 ? " and " : ", "}
                <TermLink
                  name={
                    office.name === "Temporary Rome Consul"
                      ? "Rome Consul"
                      : office.name
                  }
                  displayName={office.name}
                />{" "}
                (<SenatorLink senator={senator} />)
              </span>
            )
          })}
        .
      </p>
    )
  }

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
        {getFactionDescription()}
      </div>
      <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Tabs
          value={factionDetailTab}
          onChange={handleTabChange}
          className="px-2"
        >
          <Tab label="Overview" />
          <Tab label="Members" />
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
