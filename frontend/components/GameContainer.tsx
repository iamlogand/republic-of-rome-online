"use client"

import AvailableAction from "@/classes/AvailableAction"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import getDiceProbability from "@/utils/dice"

import ActionHandler from "./ActionHandler"
import LogList from "./LogList"

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
      <div className="mt-4 flex flex-col">
        <div className="relative">
          <div className="flex w-full flex-col gap-4 px-4 pb-8 pt-4 lg:px-10">
            <div className="mt-4 flex max-w-[1200px] flex-col gap-4 lg:grid lg:grid-cols-2">
              <div className="flex flex-col gap-4">
                <h3 className="text-xl">Sequence of play</h3>
                <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2">
                  <div>Turn {publicGameState.game?.turn}</div>
                  <div>
                    <span>{publicGameState.game?.phase} phase</span>
                  </div>
                  <div>
                    {publicGameState.game?.subPhase && (
                      <span className="flex items-center rounded-full bg-neutral-200 px-2 text-center text-sm text-neutral-600">
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
            <h3 className="mt-4 text-xl">Factions</h3>
            <div className="flex flex-col gap-4 2xl:grid 2xl:grid-cols-[repeat(auto-fill,minmax(700px,1fr))]">
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
                    <div key={index} className="flex w-full">
                      <div
                        className={`border-y border-l pl-1 ${
                          myFaction
                            ? "border-neutral-600 bg-neutral-600"
                            : "border-neutral-400 bg-neutral-300"
                        }`}
                      />
                      <div className="grow rounded-r border-y border-r border-neutral-400">
                        <div className="py-0.5">
                          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2 py-2 pl-3 pr-4 lg:pl-5 lg:pr-6">
                            <h4 className="text-lg font-semibold">
                              {faction.displayName}
                            </h4>
                            <div>{faction.player.username}</div>
                            {faction.statusItems.length > 0 &&
                              faction.statusItems.map(
                                (status: string, index: number) => (
                                  <div
                                    key={index}
                                    className="flex items-center rounded-full bg-neutral-200 px-2 text-center text-sm text-neutral-600"
                                  >
                                    {status}
                                  </div>
                                ),
                              )}
                          </div>
                          <div>
                            {senators.map((senator: Senator, index: number) => (
                              <div key={index}>
                                <hr className="my-0.5 border-neutral-300" />
                                <div className="flex flex-col gap-x-4 gap-y-2 py-2 pl-3 pr-4 lg:pl-5 lg:pr-6">
                                  <div className="flex gap-4">
                                    <span>
                                      <span>{senator.displayName} </span>
                                      <span className="text-sm text-neutral-600">
                                        ({senator.code})
                                      </span>
                                    </span>
                                    {senator.titles.length > 0 && (
                                      <>
                                        {senator.titles.map(
                                          (title: string, index: number) => (
                                            <div key={index}>{title}</div>
                                          ),
                                        )}
                                      </>
                                    )}
                                    {senator.statusItems.length > 0 && (
                                      <>
                                        {senator.statusItems.map(
                                          (status: string, index: number) => (
                                            <div
                                              key={index}
                                              className="flex items-center rounded-full bg-neutral-200 px-2 text-center text-sm text-neutral-600"
                                            >
                                              {status}
                                            </div>
                                          ),
                                        )}
                                      </>
                                    )}
                                  </div>
                                  <div className="flex flex-wrap gap-x-4 gap-y-2">
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Military
                                      </span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.military}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Oratory
                                      </span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.oratory}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Loyalty
                                      </span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.loyalty}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Influence
                                      </span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.influence}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Popularity
                                      </span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.popularity}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-neutral-600">
                                        Knights
                                      </span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.knights}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm text-neutral-600">
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
            <h3 className="mt-4 text-xl">Wars</h3>
            {publicGameState.wars.length === 0 ? (
              "There are no wars"
            ) : (
              <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[repeat(auto-fill,minmax(400px,1fr))]">
                {publicGameState.wars
                  .sort((a, b) => b.id - a.id)
                  .map((war: War, index: number) => {
                    return (
                      <div
                        key={index}
                        className="flex flex-col gap-4 rounded border border-neutral-400 px-4 py-2 lg:px-6 lg:py-4"
                      >
                        <div className="flex w-full justify-between gap-4">
                          <div className="flex flex-col gap-2">
                            <h4 className="text-lg font-semibold">
                              {war.name}
                            </h4>
                            <div className="flex flex-wrap gap-x-2 gap-y-2">
                              <div
                                className={`flex items-center rounded-full px-2 text-center text-sm ${
                                  (war.status === "Inactive" ||
                                    war.status === "Defeated") &&
                                  "bg-neutral-200 text-neutral-600"
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
                                <div className="flex items-center rounded-full bg-neutral-200 px-2 text-center text-sm text-neutral-600">
                                  Unprosecuted
                                </div>
                              )}
                              {war.undefeatedNavy && (
                                <div className="flex items-center rounded-full bg-neutral-200 px-2 text-center text-sm text-neutral-600">
                                  Undefeated navy
                                </div>
                              )}
                            </div>
                          </div>
                          <div>
                            <span className="text-sm/7 text-neutral-600">
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
                          <div className="flex flex-col flex-wrap gap-x-4 gap-y-1">
                            <div>
                              <span className="text-sm text-neutral-600">
                                Land strength
                              </span>{" "}
                              {war.landStrength}
                            </div>
                            {war.fleetSupport > 0 && (
                              <div>
                                <span className="text-sm text-neutral-600">
                                  Fleet support
                                </span>{" "}
                                {war.fleetSupport}
                              </div>
                            )}
                            {war.navalStrength > 0 && (
                              <div>
                                <span className="text-sm text-neutral-600">
                                  Naval strength
                                </span>{" "}
                                {war.navalStrength}
                              </div>
                            )}
                          </div>
                          <div>
                            <div>
                              <span className="text-sm text-neutral-600">
                                Disaster chance
                              </span>{" "}
                              {Math.round(
                                war.disasterNumbers.reduce(
                                  (acc, curr) =>
                                    acc +
                                    getDiceProbability(3, 0, { exact: curr }),
                                  0,
                                ) * 100,
                              )}
                              %
                            </div>
                            <div>
                              <span className="text-sm text-neutral-600">
                                Standoff chance
                              </span>{" "}
                              {Math.round(
                                war.standoffNumbers.reduce(
                                  (acc, curr) =>
                                    acc +
                                    getDiceProbability(3, 0, { exact: curr }),
                                  0,
                                ) * 100,
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
                <h3 className="mt-4 text-xl">
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
                      ),
                    )
                  )}
                </div>
              </>
            )}

            <div className="flex max-h-[450px] xl:hidden">
              <LogList publicGameState={publicGameState} />
            </div>
          </div>
          {privateGameState && (
            <div className="bottom-0 w-full border-t border-neutral-300 bg-blue-50/75 px-4 pb-6 pt-4 backdrop-blur-sm xl:sticky xl:rounded-tr xl:border-r xl:px-10">
              <div className="flex flex-col gap-4">
                <h3 className="text-xl">Your available actions</h3>
                <div className="flex min-h-[34px] flex-wrap gap-x-4 gap-y-2">
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
                        ),
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
