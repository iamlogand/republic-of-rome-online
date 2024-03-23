import Link from "next/link"
import Image from "next/image"
import React, { useCallback } from "react"

import Button from "@mui/material/Button"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faRightFromBracket } from "@fortawesome/free-solid-svg-icons"
import VisibilityIcon from "@mui/icons-material/Visibility"

import { useGameContext } from "@/contexts/GameContext"
import { useCookieContext } from "@/contexts/CookieContext"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import FactionLink from "@/components/FactionLink"
import SenatorLink from "@/components/SenatorLink"
import TermLink from "@/components/TermLink"
import TimeIcon from "@/images/icons/time.svg"
import VotesIcon from "@/images/icons/votes.svg"
import SecretsIcon from "@/images/icons/secrets.svg"
import AttributeFlex, { Attribute } from "@/components/AttributeFlex"
import Collection from "@/classes/Collection"
import SelectedDetail from "@/types/SelectedDetail"
import Search from "@/components/Search"

// Section showing meta info about the game
const MetaSection = () => {
  const { user, darkMode } = useCookieContext()
  const {
    game,
    latestTurn,
    latestPhase,
    latestStep,
    allPlayers,
    allFactions,
    allSenators,
    allSecrets,
    setSelectedDetail,
    setFactionDetailTab,
  } = useGameContext()

  // Get data
  const player: Player | null = user?.id
    ? allPlayers.asArray.find((p) => p.user?.id === user?.id) ?? null
    : null
  const faction: Faction | null = player?.id
    ? allFactions.asArray.find((f) => f.player === player?.id) ?? null
    : null
  const hrao: Senator | null =
    allSenators.asArray.find((s) => s.rank === 0) ?? null
  const hraoFaction: Faction | null = hrao?.faction
    ? allFactions.asArray.find((f) => f.id == hrao.faction) ?? null
    : null

  const handleSecretsClick = useCallback(() => {
    if (faction?.id)
      setSelectedDetail({
        type: "Faction",
        id: faction.id,
      } as SelectedDetail)
    setFactionDetailTab(2)
  }, [faction, setSelectedDetail, setFactionDetailTab])

  let attributeItems: Attribute[] = []
  if (faction) {
    const senators = new Collection<Senator>(
      allSenators.asArray
        .filter((s) => s.alive) // Filter by alive
        .filter((s) => s.faction === faction.id) // Filter by faction
        .sort((a, b) => a.generation - b.generation) // Sort by generation
        .sort((a, b) => a.name.localeCompare(b.name)) ?? [] // Sort by name
    )
    const totalVotes = senators.asArray.reduce(
      (total, senator) => total + senator.votes,
      0
    )
    const secrets = allSecrets.asArray.filter((s) => s.faction === faction.id)
    attributeItems = [
      { name: "votes", value: totalVotes, icon: VotesIcon },
      {
        name: "secrets",
        value: secrets.length,
        icon: SecretsIcon,
        onClick: handleSecretsClick,
      },
    ]
  }

  const getPhaseTerm = (phase: string) => {
    switch (phase) {
      case "Faction":
        return <TermLink name="Faction Phase" />
      case "Mortality":
        return <TermLink name="Mortality Phase" />
      case "Forum":
        return <TermLink name="Forum Phase" />
      case "Final Forum":
        return <TermLink name="Final Forum Phase" />
    }
  }

  if (game) {
    return (
      <section className="flex flex-col-reverse lg:flex-row gap-2 align-center justify-between rounded bg-neutral-200 dark:bg-neutral-750">
        <div className="flex-1 flex flex-col lg:flex-row gap-3 items-center justify-start">
          {faction ? (
            <div
              className="flex flex-col justify-around self-stretch px-4 py-2 rounded shadow"
              style={{
                backgroundColor: darkMode
                  ? faction.getColor(900)
                  : faction.getColor(100),
                border: `1px solid ${
                  darkMode ? faction.getColor(800) : faction.getColor(50)
                }`,
              }}
            >
              <h3 className="text-sm">Your Faction</h3>
              <div className="flex items-center gap-3">
                <div>
                  <FactionLink faction={faction} includeIcon />
                </div>
                <AttributeFlex attributes={attributeItems} />
              </div>
            </div>
          ) : (
            <div className="flex justify-center items-center self-stretch px-6 py-2 bg-neutral-100 dark:bg-neutral-650 rounded shadow">
              <VisibilityIcon style={{ marginRight: 8 }} /> Spectating
            </div>
          )}
          {hrao && (
            <div className="p-3 border border-solid border-neutral-300 dark:border-neutral-800 rounded shadow-inner bg-neutral-100 dark:bg-neutral-700">
              <span>
                The{" "}
                <TermLink
                  name="HRAO"
                  tooltipTitle="Highest Ranking Available Official"
                />{" "}
                is <SenatorLink senator={hrao} />
                {hraoFaction && (
                  <span>
                    {" "}
                    of the <FactionLink faction={hraoFaction} />
                  </span>
                )}
              </span>
            </div>
          )}
          <Search />
        </div>
        <div className="self-stretch py-3 px-4 flex gap-6 justify-between bg-neutral-50 dark:bg-neutral-650 rounded shadow">
          <div className="flex flex-col gap-2 justify-around">
            <h2 className="leading-tight m-0 text-lg">{game.name}</h2>
            <span
              title={`Step ${latestStep?.index.toString()}`}
              className="text-sm"
            >
              <Image
                src={TimeIcon}
                alt="Time icon"
                width={20}
                height={20}
                className="align-middle mt-[-4px] mb-[-2px] mr-1"
              />
              {game.end_date ? (
                <b>Game over</b>
              ) : (
                <span>
                  Turn {latestTurn?.index},{" "}
                  {latestPhase && getPhaseTerm(latestPhase.name)}
                </span>
              )}
            </span>
          </div>
          <div className="flex flex-col justify-center">
            <Button
              variant="outlined"
              LinkComponent={Link}
              href={`/games/${game.id}`}
            >
              <FontAwesomeIcon
                icon={faRightFromBracket}
                fontSize={16}
                style={{ marginRight: 8 }}
              />
              Lobby
            </Button>
          </div>
        </div>
      </section>
    )
  } else {
    return null
  }
}

export default MetaSection
