"use client"

import AvailableAction from "@/classes/AvailableAction"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import Senator from "@/classes/Senator"
import PublicGameState from "@/classes/PublicGameState"
import ActionHandler from "./ActionHandler"
import War from "@/classes/War"
import getDiceProbability from "@/utils/dice"
import LogList from "./Logs"

interface GameContainerProps {
  publicGameState: PublicGameState
  privateGameState: PrivateGameState | undefined
}

const GameContainer = ({
  publicGameState,
  privateGameState,
}: GameContainerProps) => {
  return (
    <div>
      <div className="flex flex-col">
        <div className="relative">
          <div className="w-full px-4 lg:px-10 pt-4 pb-8 flex flex-col gap-4">
            <div className="max-w-[1200px] mt-4 flex flex-col gap-4 lg:grid lg:grid-cols-2">
              <div className="flex flex-col gap-4">
                <h3 className="text-xl">Sequence of play</h3>
                <div className="flex gap-x-4 gap-y-2 items-baseline flex-wrap">
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
              </div>
              <div className="flex flex-col gap-4">
                <h3 className="text-xl">Rome</h3>
                <div className="flex gap-4">
                  <div>
                    State treasury: {publicGameState.game?.stateTreasury}T
                  </div>
                  <div>Unrest: {publicGameState.game?.unrest}</div>
                </div>
              </div>
            </div>
            <h3 className="text-xl mt-4">Factions</h3>
            <div className="flex flex-col lg:grid lg:grid-cols-[repeat(auto-fit,minmax(700px,1fr))] gap-4">
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
                    <div key={index} className="w-full flex">
                      <div
                        className={`pl-1 border-y border-l ${
                          myFaction
                            ? "bg-neutral-600 border-neutral-600"
                            : "bg-neutral-300 border-neutral-400"
                        }`}
                      />
                      <div className="grow border-y border-r rounded-r border-neutral-400">
                        <div className="py-0.5">
                          <div className="pl-3 pr-4 lg:pl-5 lg:pr-6 py-2 flex gap-x-4 gap-y-2 flex-wrap items-baseline">
                            <h4 className="font-semibold text-lg">
                              {faction.displayName}
                            </h4>
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
                                <div className="flex flex-col pl-3 pr-4 lg:pl-5 lg:pr-6 py-2 gap-x-4 gap-y-2">
                                  <div className="flex gap-4">
                                    <span>
                                      <span>{senator.displayName} </span>
                                      <span className="text-neutral-600 text-sm">
                                        ({senator.code})
                                      </span>
                                    </span>
                                    {senator.titles.length > 0 && (
                                      <>
                                        {senator.titles.map(
                                          (title: string, index: number) => (
                                            <div key={index}>{title}</div>
                                          )
                                        )}
                                      </>
                                    )}
                                    {senator.statusItems.length > 0 && (
                                      <>
                                        {senator.statusItems.map(
                                          (status: string, index: number) => (
                                            <div
                                              key={index}
                                              className="text-sm px-2 rounded-full bg-neutral-200 text-neutral-600 flex items-center text-center"
                                            >
                                              {status}
                                            </div>
                                          )
                                        )}
                                      </>
                                    )}
                                  </div>
                                  <div className="flex gap-x-4 gap-y-2 flex-wrap">
                                    <div>
                                      <span className="text-neutral-600 text-sm">
                                        Military
                                      </span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.military}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-neutral-600 text-sm">
                                        Oratory
                                      </span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.oratory}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-neutral-600 text-sm">
                                        Loyalty
                                      </span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.loyalty}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-neutral-600 text-sm">
                                        Influence
                                      </span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.influence}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-neutral-600 text-sm">
                                        Popularity
                                      </span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.popularity}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-neutral-600 text-sm">
                                        Knights
                                      </span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.knights}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-neutral-600 text-sm">
                                        Votes
                                      </span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.votes}
                                      </span>
                                    </div>
                                    <div className="w-7" dir="rtl">
                                      {senator.talents}T
                                    </div>
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
            </div>
            <h3 className="text-xl mt-4">Wars</h3>
            {publicGameState.wars.length === 0 ? (
              "There are no wars"
            ) : (
              <div className="flex flex-col lg:grid lg:grid-cols-[repeat(auto-fit,minmax(400px,1fr))] gap-4">
                {publicGameState.wars
                  .sort((a, b) => a.name.localeCompare(b.name))
                  .map((war: War, index: number) => {
                    return (
                      <div
                        key={index}
                        className="px-4 lg:px-6 py-2 lg:py-4 border border-neutral-400 rounded flex flex-col gap-4"
                      >
                        <div className="w-full flex justify-between gap-4">
                          <div className="flex flex-col gap-2">
                            <h4 className="font-semibold text-lg">
                              {war.name}
                            </h4>
                            <div className="flex gap-x-2 gap-y-2 flex-wrap">
                              <div
                                className={`text-sm px-2 rounded-full flex items-center text-center ${
                                  (war.status === "Inactive" ||
                                    war.status === "Defeated") &&
                                  " bg-neutral-200 text-neutral-600"
                                } ${
                                  war.status === "Active" &&
                                  "bg-red-200 text-red-900"
                                } ${
                                  war.status === "Imminent" &&
                                  "bg-amber-200 text-amber-900"
                                }`}
                              >
                                {war.status}
                              </div>
                              {war.unprosecuted && (
                                <div className="text-sm px-2 rounded-full bg-neutral-200 text-neutral-600 flex items-center text-center">
                                  Unprosecuted
                                </div>
                              )}
                              {war.undefeatedNavy && (
                                <div className="text-sm px-2 rounded-full bg-neutral-200 text-neutral-600 flex items-center text-center">
                                  Undefeated navy
                                </div>
                              )}
                            </div>
                          </div>
                          <div>
                            <span className="text-neutral-600 text-sm/7">
                              Spoils
                            </span>{" "}
                            {war.spoils}T
                          </div>
                        </div>
                        {(war.seriesName || war.famine) && (
                          <div className="flex flex-col gap-1">
                            {war.seriesName && (
                              <div className="">
                                Part of the {war.seriesName} Wars series
                              </div>
                            )}
                            {war.famine && (
                              <div className="text-sm">
                                Causes famine when active
                              </div>
                            )}
                          </div>
                        )}
                        <div className="grid grid-cols-2">
                          <div className="flex flex-col gap-x-4 gap-y-1 flex-wrap">
                            <div>
                              <span className="text-neutral-600 text-sm">
                                Land strength
                              </span>{" "}
                              {war.landStrength}
                            </div>
                            {war.fleetSupport > 0 && (
                              <div>
                                <span className="text-neutral-600 text-sm">
                                  Fleet support
                                </span>{" "}
                                {war.fleetSupport}
                              </div>
                            )}
                            {war.navalStrength > 0 && (
                              <div>
                                <span className="text-neutral-600 text-sm">
                                  Naval strength
                                </span>{" "}
                                {war.navalStrength}
                              </div>
                            )}
                          </div>
                          <div>
                            <div>
                              <span className="text-neutral-600 text-sm">
                                Disaster chance
                              </span>{" "}
                              {Math.round(
                                war.disasterNumbers.reduce(
                                  (acc, curr) =>
                                    acc +
                                    getDiceProbability(3, 0, { exact: curr }),
                                  0
                                ) * 100
                              )}
                              %
                            </div>
                            <div>
                              <span className="text-neutral-600 text-sm">
                                Standoff chance
                              </span>{" "}
                              {Math.round(
                                war.standoffNumbers.reduce(
                                  (acc, curr) =>
                                    acc +
                                    getDiceProbability(3, 0, { exact: curr }),
                                  0
                                ) * 100
                              )}
                              %
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            )}
            {privateGameState?.faction && (
              <>
                <h3 className="text-xl mt-4">
                  {privateGameState?.faction.displayName} secrets
                </h3>
                <p>Faction treasury: {privateGameState?.faction.treasury}</p>
                <div>
                  Cards:{" "}
                  {privateGameState?.faction.cards.length === 0 ? (
                    <span className="text-neutral-600">None</span>
                  ) : (
                    privateGameState?.faction.cards.map(
                      (card: string, index: number) => (
                        <span key={index}>
                          <span>{card}</span>
                          {index <
                            privateGameState?.faction!.cards.length - 1 && (
                            <span>, </span>
                          )}
                        </span>
                      )
                    )
                  )}
                </div>
              </>
            )}

            <div className="flex lg:hidden max-h-[450px]">
              <LogList publicGameState={publicGameState} />
            </div>
          </div>
          {privateGameState && (
            <div className="lg:sticky w-full bottom-0 px-4 lg:px-10 pt-4 pb-6 bg-blue-50/75 backdrop-blur-sm border-t lg:border-r border-neutral-300 lg:rounded-tr">
              <div className="flex flex-col gap-4">
                <h3 className="text-xl">Your available actions</h3>
                <div className="min-h-[34px] flex gap-x-4 gap-y-2 flex-wrap">
                  {privateGameState?.availableActions.length > 0 ? (
                    privateGameState?.availableActions
                      .sort((a, b) => a.position - b.position)
                      .map(
                        (availableAction: AvailableAction, index: number) => (
                          <ActionHandler
                            key={index}
                            availableAction={availableAction}
                            publicGameState={publicGameState}
                            privateGameState={privateGameState}
                          />
                        )
                      )
                  ) : (
                    <p className="text-neutral-600">None right now</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default GameContainer
