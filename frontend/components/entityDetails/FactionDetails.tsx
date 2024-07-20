import { Tab, Tabs } from "@mui/material"

import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import SenatorList from "@/components/SenatorList"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import VotesIcon from "@/images/icons/votes.svg"
import SenatorIcon from "@/images/icons/senator.svg"
import SecretsIcon from "@/images/icons/secrets.svg"
import AttributeGrid, { Attribute } from "@/components/AttributeGrid"
import SenatorPortrait from "@/components/SenatorPortrait"
import Title from "@/classes/Title"
import SenatorLink from "@/components/SenatorLink"
import TermLink from "@/components/TermLink"
import SecretList from "@/components/SecretList"
import { useCookieContext } from "@/contexts/CookieContext"
import CustomizeFactionName from "@/components/CustomizeFactionName"
import FactionName from "@/components/FactionName"

// Detail section content for a faction
const FactionDetails = () => {
  const { user } = useCookieContext()
  const {
    allPlayers,
    allFactions,
    allSenators,
    allTitles,
    selectedDetail,
    factionDetailTab,
    setFactionDetailTab,
    allSecrets,
  } = useGameContext()

  // Get faction-specific data
  let senators: Collection<Senator> = new Collection<Senator>([])
  if (selectedDetail && selectedDetail.type == "Faction") {
    senators = new Collection<Senator>(
      // Filter by faction and alive, then sort by name
      allSenators.asArray
        .filter((s) => s.faction === selectedDetail.id && s.alive === true)
        .sort((a, b) => a.name.localeCompare(b.name))
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
  const combinedPersonalTreasuries = senators.asArray.reduce(
    (total, senator) => total + senator.personalTreasury,
    0
  )
  const totalVotes = senators.asArray.reduce(
    (total, senator) => total + senator.votes,
    0
  )
  const secrets = allSecrets.asArray.filter((s) => s.faction === faction?.id)

  // Get faction-specific data for the current user
  const currentPlayer: Player | null = user?.id
    ? allPlayers.asArray.find((p) => p.user?.id === user?.id) ?? null
    : null
  const currentFaction: Faction | null = currentPlayer?.id
    ? allFactions.asArray.find((f) => f.player === currentPlayer?.id) ?? null
    : null

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

  // Switch to the overview tab if secret tab is selected and the current user is not in this faction
  if (
    factionDetailTab === 2 &&
    currentFaction &&
    faction &&
    currentFaction.id !== faction.id
  ) {
    setFactionDetailTab(0)
  }

  // Attribute data
  const attributes: Attribute[] = [
    {
      name: "Senators",
      value: senators.allIds.length,
      icon: SenatorIcon,
      termLinkName: "Senator",
    },
    {
      name: "Combined Influence",
      value: totalInfluence,
      icon: InfluenceIcon,
      fontSize: 14,
      termLinkName: "Influence",
    },
    {
      name: "Personal Treasuries",
      value: combinedPersonalTreasuries,
      icon: TalentsIcon,
      fontSize: 14,
      tooltipTitle: "Combined Personal Treasuries",
      termLinkName: "Personal Treasury",
    },
    {
      name: "Combined Votes",
      value: totalVotes,
      icon: VotesIcon,
      fontSize: 14,
      termLinkName: "Votes",
    },
    {
      name: "Secrets",
      value: secrets.length,
      icon: SecretsIcon,
      termLinkName: "Secret",
    },
  ]

  // If there is no faction selected, render nothing
  if (!faction) return null

  // GetJSX for the faction description
  const getFactionDescription = () => {
    const significantSenatorCount = hraoSenator ? 1 : 0 + majorOffices.length
    return (
      <p>
        {currentFaction && currentFaction?.id === faction.id ? (
          "Your"
        ) : (
          <span>The {faction.getName()}</span>
        )}{" "}
        <TermLink name="Faction" />
        {factionLeader && (
          <span>
            , led by <SenatorLink senator={factionLeader} />,
          </span>
        )}{" "}
        has {senators.allIds.length} member{senators.allIds.length !== 1 && "s"}
        {hraoSenator && (
          <span>
            , including the <TermLink name="HRAO" />
            {majorOffices.length == 0 && (
              <span>
                {": "}
                <SenatorLink senator={hraoSenator} />
              </span>
            )}
          </span>
        )}
        {majorOffices.length > 0 &&
          majorOffices.map((office, index) => {
            const senator = senators.asArray.find((s) => s.id == office.senator)
            if (!senator) return null
            return (
              <span key={index}>
                {index === significantSenatorCount - 1 ? " and " : ", "}
                <TermLink name={office.name} displayName={office.name} />
                {": "}
                <SenatorLink senator={senator} />
              </span>
            )
          })}
        .
      </p>
    )
  }

  return (
    <div className="h-full box-border flex flex-col overflow-y-auto">
      <div className="p-4 flex flex-col gap-4">
        <div className="flex justify-between flex-wrap gap-2">
          <div className="flex">
            <span className="mr-2 mt-1">
              <FactionIcon faction={faction} size={26} />
            </span>
            <h4 className="text-lg">
              {faction.customName ? (
                <span>
                  <b>
                    <FactionName faction={faction} />
                  </b>{" "}
                  ({faction.getName()} Faction)
                </span>
              ) : (
                <b>
                  <FactionName faction={faction} />
                </b>
              )}{" "}
              of {player ? player.user?.username : "unknown"}
            </h4>
          </div>
          {currentFaction &&
            currentFaction.id === faction.id &&
            !faction.customName && <CustomizeFactionName faction={faction} />}
        </div>

        {getFactionDescription()}
      </div>
      <div className="border-0 border-b border-solid border-neutral-200 dark:border-neutral-750">
        <Tabs
          value={factionDetailTab}
          onChange={handleTabChange}
          className="px-4"
        >
          <Tab label="Overview" />
          <Tab label="Members" />
          {currentFaction && currentFaction.id === faction.id && (
            <Tab label="Secrets" />
          )}
        </Tabs>
      </div>
      <div className="grow overflow-y-auto bg-neutral-50 dark:bg-neutral-700 shadow-inner">
        {factionDetailTab === 0 && (
          <div className="p-4 flex flex-col gap-6">
            <div className="p-2">
              <AttributeGrid attributes={attributes} />
            </div>
            <div className="flex flex-wrap gap-2">
              {senators.asArray.map((senator: Senator) => (
                <SenatorPortrait
                  key={senator.id}
                  senator={senator}
                  size={90}
                  selectable
                  summary
                />
              ))}
            </div>
          </div>
        )}
        {factionDetailTab === 1 && (
          <div className="h-full p-4 box-border">
            <SenatorList faction={faction} selectable border />
          </div>
        )}
        {factionDetailTab === 2 &&
          currentFaction &&
          currentFaction.id === faction.id && (
            <div className="h-full p-4 box-border">
              <div className="mb-4">
                Your Faction has {secrets.length}{" "}
                <TermLink name="Secret" plural={secrets.length != 1} />.
              </div>
              <SecretList faction={faction} />
            </div>
          )}
      </div>
    </div>
  )
}

export default FactionDetails
