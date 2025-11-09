"use client"

import { useCallback, useState } from "react"

import AvailableAction from "@/classes/AvailableAction"
import Campaign from "@/classes/Campaign"
import CombatCalculation from "@/classes/CombatCalculation"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import getDiceProbability from "@/utils/dice"
import { forceListToString } from "@/utils/forceLists"

import ActionHandler, { ActionSelection } from "./ActionHandler"
import CombatCalculator from "./CombatCalculator"
import LogList from "./LogList"

interface GameContainerProps {
  publicGameState: PublicGameState
  combatCalculations: CombatCalculation[]
  updateCombatCalculations: (combatCalculations: CombatCalculation[]) => void
  privateGameState: PrivateGameState | undefined
}

const GameContainer = ({
  publicGameState,
  combatCalculations,
  updateCombatCalculations,
  privateGameState,
}: GameContainerProps) => {
  const [selectionMap, setSelectionMap] = useState<
    Record<string, ActionSelection>
  >({})

  const [expandedActionId, setExpandedActionId] = useState<number | null>(null)

  const updateSelection = useCallback(
    (
      id: string | number,
      newSelection:
        | ActionSelection
        | ((prev: ActionSelection | undefined) => ActionSelection),
    ) => {
      setSelectionMap((prev) => ({
        ...prev,
        [id]:
          typeof newSelection === "function"
            ? newSelection(prev[id])
            : newSelection,
      }))
    },
    [],
  )

  const handleTransferToProposal = useCallback(
    (calculation: CombatCalculation) => {
      if (!privateGameState) return

      const deployAction = privateGameState.availableActions.find(
        (action) => action.name === "Propose deploying forces",
      )
      if (!deployAction) return

      const newSelection: ActionSelection = {}

      if (calculation.commander !== null) {
        newSelection["Commander"] = calculation.commander
      }

      if (calculation.war !== null) {
        newSelection["Target war"] = calculation.war
      }

      if (calculation.legions > 0 || calculation.veteranLegions > 0) {
        const availableRegularLegions = publicGameState.legions
          .filter(
            (l) => !l.veteran && l.campaign === null && l.allegiance === null,
          )
          .sort((a, b) => a.id - b.id)
          .slice(0, calculation.legions)
          .map((l) => l.id)

        const availableVeteranLegions = publicGameState.legions
          .filter(
            (l) => l.veteran && l.campaign === null && l.allegiance === null,
          )
          .sort((a, b) => a.id - b.id)
          .slice(0, calculation.veteranLegions)
          .map((l) => l.id)

        newSelection["Legions"] = [
          ...availableRegularLegions,
          ...availableVeteranLegions,
        ]
      }

      if (calculation.fleets > 0) {
        const availableFleets = publicGameState.fleets
          .filter((f) => f.campaign === null)
          .sort((a, b) => a.id - b.id)
          .slice(0, calculation.fleets)
          .map((f) => f.id)

        newSelection["Fleets"] = availableFleets
      }

      updateSelection(deployAction.id, newSelection)

      setExpandedActionId(deployAction.id)
    },
    [privateGameState, publicGameState, updateSelection],
  )

  const reserveLegions = publicGameState.legions.filter(
    (l) => l.campaign == null,
  )
  const reserveFleets = publicGameState.fleets.filter((f) => f.campaign == null)

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
                        {publicGameState.game?.subPhase}
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
                  <div>Unrest level: {publicGameState.game?.unrest}</div>
                </div>

                <div>
                  Reserve forces: {reserveLegions.length} legions
                  {reserveLegions.length > 0 && (
                    <> ({forceListToString(reserveLegions)})</>
                  )}
                  {reserveLegions.length > 0 &&
                    reserveFleets.length > 0 &&
                    " and "}
                  {reserveFleets.length} fleets
                  {reserveFleets.length > 0 && (
                    <> ({forceListToString(reserveFleets)})</>
                  )}
                </div>
              </div>
            </div>

            <h3 className="mt-4 text-xl">Tools</h3>
            <div className="flex min-h-[34px] flex-wrap gap-x-4 gap-y-2">
              <CombatCalculator
                publicGameState={publicGameState}
                privateGameState={privateGameState}
                combatCalculations={combatCalculations}
                updateCombatCalculations={updateCombatCalculations}
                onTransferToProposal={handleTransferToProposal}
              />
            </div>

            {publicGameState.game?.phase === "Senate" && (
              <>
                <h3 className="mt-4 text-xl">Senate</h3>
                <div className="flex flex-col gap-2">
                  <div>
                    Current proposal:{" "}
                    {publicGameState.game?.currentProposal ? (
                      <b>{publicGameState.game?.currentProposal}</b>
                    ) : (
                      <span className="text-neutral-600">None</span>
                    )}
                  </div>
                  {publicGameState.game?.currentProposal && (
                    <div className="flex gap-4">
                      <span className="inline-block w-14">
                        Yea: {publicGameState.game?.votes_yea}
                      </span>
                      <span className="inline-block w-14">
                        Nay: {publicGameState.game?.votes_nay}
                      </span>
                      <span>
                        Pending: {publicGameState.game?.votes_pending}
                      </span>
                    </div>
                  )}
                  {publicGameState.game?.defeated_proposals.length > 0 && (
                    <>
                      Defeated proposals:
                      <ul>
                        {publicGameState.game?.defeated_proposals.map(
                          (proposal, index) => (
                            <li key={index} className="ml-10 list-disc">
                              {proposal}
                            </li>
                          ),
                        )}
                      </ul>
                    </>
                  )}
                </div>
              </>
            )}

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
                            ? "border-[#630330] bg-[#630330]"
                            : "border-neutral-400 bg-neutral-200"
                        }`}
                      />
                      <div className="grow rounded-r border-y border-r border-neutral-400">
                        <div className="py-0.5">
                          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2 py-2 pl-3 pr-4 text-[#630330] lg:pl-5 lg:pr-6">
                            <h4 className="text-xl font-semibold">
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
                                  <div className="flex items-baseline justify-between gap-4">
                                    <div className="flex flex-wrap gap-x-4">
                                      <span>
                                        <span className="font-semibold">
                                          {senator.displayName}
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
                                    {senator.location !== "Rome" && (
                                      <div>In {senator.location}</div>
                                    )}
                                  </div>
                                  <div className="flex flex-wrap gap-x-4 gap-y-2 text-neutral-600">
                                    <div>
                                      <span className="text-sm">Military</span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.military}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm">Oratory</span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.oratory}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm">Loyalty</span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.loyalty}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm">Influence</span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.influence}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm">
                                        Popularity
                                      </span>{" "}
                                      <span className="inline-block w-5">
                                        {senator.popularity}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm">Knights</span>{" "}
                                      <span className="inline-block w-3">
                                        {senator.knights}
                                      </span>
                                    </div>
                                    <div>
                                      <span className="text-sm">Votes</span>{" "}
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
                  .sort((a, b) => a.id - b.id)
                  .map((war: War, index: number) => {
                    return (
                      <div
                        key={index}
                        className="flex flex-col gap-4 rounded border border-neutral-400 px-4 py-2 lg:px-6 lg:py-4"
                      >
                        <div className="flex w-full justify-between gap-4">
                          <div className="flex flex-col gap-2">
                            <h4 className="text-lg font-semibold">
                              {war.name}{" "}
                              <span className="text-base font-normal text-neutral-600">
                                in {war.location}
                              </span>
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
                              {(() => {
                                let total = 0
                                war.disasterNumbers.forEach((curr) => {
                                  total += getDiceProbability(3, 0, {
                                    exacts: [curr],
                                  })
                                })
                                return Math.round(total * 100)
                              })()}
                              %
                            </div>
                            <div>
                              <span className="text-sm text-neutral-600">
                                Standoff chance
                              </span>{" "}
                              {(() => {
                                let total = 0
                                war.standoffNumbers.forEach((curr) => {
                                  total += getDiceProbability(3, 0, {
                                    exacts: [curr],
                                  })
                                })
                                return Math.round(total * 100)
                              })()}
                              %
                            </div>
                          </div>
                        </div>
                      </div>
                    )
                  })}
              </div>
            )}

            <h3 className="mt-4 text-xl">Campaigns</h3>
            {publicGameState.campaigns.length === 0 ? (
              "There are no campaigns"
            ) : (
              <div className="flex flex-col gap-4 lg:grid lg:grid-cols-[repeat(auto-fill,minmax(400px,1fr))]">
                {publicGameState.campaigns
                  .sort((a, b) => a.id - b.id)
                  .map((campaign: Campaign, index: number) => {
                    const war = publicGameState.wars.find(
                      (w) => w.id === campaign.war,
                    )
                    const commander = publicGameState.senators.find(
                      (s) => s.id === campaign.commander,
                    )
                    const legions = publicGameState.legions.filter(
                      (l) => l.campaign === campaign.id,
                    )
                    const fleets = publicGameState.fleets.filter(
                      (f) => f.campaign === campaign.id,
                    )

                    return (
                      <div
                        key={index}
                        className="flex flex-col gap-4 rounded border border-neutral-400 px-4 py-2 lg:px-6 lg:py-4"
                      >
                        <div className="flex w-full items-baseline justify-between gap-4">
                          <h4 className="text-lg font-semibold">
                            {commander?.displayName}&apos;s Campaign{" "}
                            <span className="text-base font-normal text-neutral-600">
                              in {war?.location}
                            </span>
                          </h4>
                          <div>{war?.name}</div>
                        </div>
                        <p>
                          <span>{commander?.displayName} commands </span>
                          {legions && legions.length > 0 && (
                            <span>
                              {legions.length}{" "}
                              {legions.length > 1 ? "legions" : "legion"}
                              <> ({forceListToString(legions)})</>
                            </span>
                          )}
                          {fleets &&
                            fleets.length > 0 &&
                            legions &&
                            legions.length > 0 && <span> and </span>}
                          {fleets && fleets.length > 0 && (
                            <span>
                              {fleets.length}{" "}
                              {fleets.length > 1 ? "fleets" : "fleet"}
                              <> ({forceListToString(fleets)})</>
                            </span>
                          )}
                        </p>
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
                        (availableAction: AvailableAction, index: number) => {
                          const id = availableAction.id ?? index
                          const currentSelection = selectionMap[id] ?? {}
                          return (
                            <ActionHandler
                              key={id}
                              availableAction={availableAction}
                              publicGameState={publicGameState}
                              selection={currentSelection}
                              setSelection={(newSelection) =>
                                updateSelection(id, newSelection)
                              }
                              isExpanded={expandedActionId === id}
                              setIsExpanded={(expanded) =>
                                setExpandedActionId(expanded ? id : null)
                              }
                            />
                          )
                        },
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
