import Link from "next/link"
import Image from "next/image"
import React from "react"

import Button from "@mui/material/Button"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faRightFromBracket } from "@fortawesome/free-solid-svg-icons"

import { useGameContext } from "@/contexts/GameContext"
import { useAuthContext } from "@/contexts/AuthContext"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import FactionLink from "@/components/FactionLink"
import SenatorLink from "@/components/SenatorLink"
import TermLink from "@/components/TermLink"
import DeveloperTools from "@/components/DeveloperTools"
import TimeIcon from "@/images/icons/time.svg"

// Section showing meta info about the game
const MetaSection = () => {
  const { user } = useAuthContext()
  const {
    game,
    latestTurn,
    latestPhase,
    latestStep,
    allPlayers,
    allFactions,
    allSenators,
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

  if (game && latestStep && latestTurn && latestPhase) {
    return (
      <section className="flex flex-col-reverse lg:flex-row gap-2 align-center justify-between rounded bg-stone-200">
        <div className="flex-1 p-3 flex flex-col lg:flex-row gap-3 items-center justify-start">
          <DeveloperTools />
          {faction && (
            <div className="p-3 border border-solid border-stone-300 rounded shadow-inner bg-stone-100">
              <span>
                Playing as the <FactionLink faction={faction} includeIcon />
              </span>
            </div>
          )}
          {hrao && (
            <div className="p-3 border border-solid border-stone-300 rounded shadow-inner bg-stone-100">
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
                    of <FactionLink faction={hraoFaction} includeIcon />
                  </span>
                )}
              </span>
            </div>
          )}
        </div>
        <div className="self-stretch py-3 px-6 flex gap-6 justify-between bg-stone-50 rounded shadow">
          <div className="flex flex-col gap-2">
            <h2 className="leading-tight m-0 text-lg">{game.name}</h2>
            <span
              title={`Step ${latestStep?.index.toString()}`}
              style={{ fontSize: 14 }}
            >
              <Image
                src={TimeIcon}
                alt="Time icon"
                width={20}
                height={20}
                className="align-middle mt-[-4px] mb-[-2px] mr-1"
              />
              Turn {latestTurn.index}, {latestPhase.name} Phase
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
