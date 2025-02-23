"use client"

import AvailableAction from "@/classes/AvailableAction"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import Senator from "@/classes/Senator"
import PublicGameState from "@/classes/PublicGameState"
import ActionHandler from "./ActionHandler"
import Log from "@/classes/Log"
import { compareDates, formatDate } from "@/utils/date"

interface GameContainerProps {
  publicGameState: PublicGameState
  privateGameState: PrivateGameState | undefined
}

const GameContainer = ({
  publicGameState,
  privateGameState,
}: GameContainerProps) => {
  return (
    <div className="px-6 py-4 flex flex-col gap-4 mb-12">
      <div className="flex flex-col gap-4">
        <h3 className="text-xl mt-4">Sequence of play</h3>
        <div className="flex gap-4 items-baseline flex-wrap">
          <div>Turn {publicGameState.game?.turn}</div>
          <div>
            <span>{publicGameState.game?.phase} phase</span>
          </div>
          <div>
            {publicGameState.game?.subPhase && (
              <span className="text-sm px-2 rounded-full bg-neutral-200 text-neutral-600 flex items-center text-center">
                {" "}
                Sub-phase: {publicGameState.game?.subPhase}
              </span>
            )}
          </div>
        </div>
        <h3 className="text-xl mt-4">Your available actions</h3>
        <div className="min-h-[34px] flex gap-x-4 gap-y-2 flex-wrap">
          {privateGameState && privateGameState?.availableActions.length > 0
            ? privateGameState?.availableActions.map(
                (availableAction: AvailableAction, index: number) => (
                  <ActionHandler
                    key={index}
                    availableAction={availableAction}
                    publicGameState={publicGameState}
                    privateGameState={privateGameState}
                  />
                )
              )
            : "-"}
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <h3 className="text-xl mt-4">Logs</h3>
        <div className="border border-neutral-400 rounded overflow-hidden">
          <div className="max-h-[200px] overflow-auto px-4 py-1 flex flex-col-reverse gap-1">
            {publicGameState?.logs &&
              publicGameState.logs
                .sort((a, b) => {
                  const dateComparison = compareDates(b.createdOn, a.createdOn)
                  if (dateComparison !== 0) {
                    return dateComparison
                  }
                  return a.id - b.id
                })
                .map((log: Log, index: number) => {
                  console.log(log)
                  return (
                    <div
                      key={index}
                      className="flex flex-col lg:flex-row gap-x-4"
                    >
                      <div className="flex flex-col sm:flex-row gap-x-2">
                        <div className="text-neutral-500 whitespace-nowrap ">
                          {formatDate(log.createdOn)}
                        </div>
                        <div className="flex gap-x-2">
                          <div className="text-neutral-500 whitespace-nowrap ">
                            Turn {log.turn}
                          </div>
                          <div className="text-neutral-500 whitespace-nowrap ">
                            {log.phase} phase
                          </div>
                        </div>
                      </div>
                      <div>{log.text}</div>
                    </div>
                  )
                })}
          </div>
        </div>
      </div>
      <h3 className="text-xl mt-4">Rome</h3>
      <div>State treasury: {publicGameState.game?.stateTreasury}</div>
      <h3 className="text-xl mt-4">Factions</h3>
      {publicGameState.factions
        .sort((a, b) => a.position - b.position)
        .map((faction: Faction, index: number) => {
          const senators = publicGameState.senators
            .filter((s) => s.faction === faction.id && s.alive)
            .sort((a, b) => a.name.localeCompare(b.name))
          const myFaction =
            privateGameState?.faction &&
            privateGameState?.faction.id === faction.id
          return (
            <div key={index} className="flex">
              <div
                className={`pl-1 border-y border-l ${
                  myFaction
                    ? "bg-neutral-500 border-neutral-500"
                    : "bg-neutral-300 border-neutral-400"
                }`}
              />
              <div className="grow border-y border-r rounded-r border-neutral-400">
                <div className="py-0.5">
                  <div className="pl-3 pr-4 py-1 flex gap-x-4 gap-y-1 flex-wrap">
                    <h4 className="font-semibold">{faction.displayName}</h4>
                    <div>{faction.player.username}</div>
                    {faction.statusItems.length > 0 &&
                      faction.statusItems.map(
                        (status: string, index: number) => (
                          <div
                            key={index}
                            className="text-sm px-2 rounded-full bg-neutral-200 text-neutral-600 flex items-center text-center"
                          >
                            {status}
                          </div>
                        )
                      )}
                  </div>
                  <div>
                    {senators.map((senator: Senator, index: number) => (
                      <div key={index}>
                        <hr className="my-0.5 border-neutral-300" />
                        <div className="flex flex-col sm:flex-row pl-3 pr-4 py-1 gap-x-8 gap-y-1">
                          <div className="sm:min-w-[200px]">
                            <p className="">
                              {senator.displayName}{" "}
                              <span className="text-neutral-500 text-sm">
                                ({senator.code})
                              </span>
                            </p>
                          </div>
                          <div className="flex gap-x-4 gap-y-1 flex-wrap">
                            <div className="flex gap-x-4 gap-y-1 flex-wrap">
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Military
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.military}
                                </span>
                              </div>
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Oratory
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.oratory}
                                </span>
                              </div>
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Loyalty
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.loyalty}
                                </span>
                              </div>
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Influence
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.influence}
                                </span>
                              </div>
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Popularity
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.popularity}
                                </span>
                              </div>
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Knights
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.knights}
                                </span>
                              </div>
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Votes
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.votes}
                                </span>
                              </div>
                              <div>
                                <span className="text-neutral-500 text-sm">
                                  Talents
                                </span>{" "}
                                <span className="inline-block w-[15px]">
                                  {senator.talents}
                                </span>
                              </div>
                            </div>

                            {senator.titles.length > 0 && (
                              <div className="flex gap-x-4 gap-y-1 flex-wrap">
                                {senator.titles
                                  .sort((a, b) => a.localeCompare(b))
                                  .map((title: string, index: number) => (
                                    <div key={index}>{title}</div>
                                  ))}
                              </div>
                            )}
                            {senator.statusItems.length > 0 && (
                              <div className="flex gap-x-4 gap-y-1 flex-wrap">
                                {senator.statusItems
                                  .sort((a, b) => a.localeCompare(b))
                                  .map((status: string, index: number) => (
                                    <div
                                      key={index}
                                      className="text-sm px-2 rounded-full bg-neutral-200 text-neutral-600 flex items-center text-center"
                                    >
                                      {status}
                                    </div>
                                  ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      {privateGameState?.faction && (
        <>
          <h3 className="text-xl mt-4">
            {privateGameState?.faction.displayName}
          </h3>
          <p>Faction treasury: {privateGameState?.faction.treasury}</p>
          <div>
            Cards:{" "}
            {privateGameState?.faction.cards
              ? privateGameState?.faction.cards.map(
                  (card: string, index: number) => (
                    <span key={index}>
                      <span>{card}</span>
                      {index < privateGameState?.faction!.cards.length - 1 && (
                        <span>, </span>
                      )}
                    </span>
                  )
                )
              : "-"}
          </div>
        </>
      )}
    </div>
  )
}

export default GameContainer
