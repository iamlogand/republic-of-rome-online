import Campaign from "@/classes/Campaign"
import EnemyLeader from "@/classes/EnemyLeader"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"
import Popover from "@/components/Popover"
import SenatorDisplay from "@/components/SenatorDisplay"
import getDiceProbability from "@/helpers/dice"
import { forceListToString } from "@/helpers/forceLists"
import { toFamilyAdjective, toSentenceCase } from "@/helpers/text"

interface Props {
  publicGameState: PublicGameState
  privateGameState: PrivateGameState | undefined
}

const GameMain = ({ publicGameState, privateGameState }: Props) => {
  const game = publicGameState.game!

  const deceasedSenators = publicGameState.senators
    .filter((s) => !s.alive)
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const unalignedSenators = publicGameState.senators
    .filter((s) => s.faction === null && s.alive)
    .sort((a, b) => a.familyName.localeCompare(b.familyName))

  const showUnalignedSection =
    unalignedSenators.length > 0 || deceasedSenators.length > 0

  const showConflictsSection =
    publicGameState.wars.length > 0 || publicGameState.enemyLeaders.length > 0

  return (
    <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-10 py-6">
      {/* Factions */}
      <div className="flex flex-col gap-2">
        <div className="flex items-baseline justify-between">
          <h3 className="text-xl">Factions</h3>
          {game.concessions.length > 0 && (
            <Popover
              align="right"
              trigger={
                <span className="px-2 text-sm text-neutral-600">
                  {game.concessions.length === 1
                    ? "1 unawarded concession"
                    : `${game.concessions.length} unawarded concessions`}
                </span>
              }
            >
              <ul className="flex flex-col gap-1">
                {game.concessions.map((concession, index) => (
                  <li
                    key={index}
                    className="ml-6 list-disc first-letter:uppercase"
                  >
                    {concession}
                    {!game.availableConcessions.includes(concession) && (
                      <span className="text-neutral-500"> (unavailable)</span>
                    )}
                  </li>
                ))}
              </ul>
            </Popover>
          )}
        </div>
        <div className="grid grid-cols-[repeat(auto-fill,minmax(700px,1fr))] gap-4">
          {publicGameState.factions
            .sort((a, b) => a.position - b.position)
            .map((faction: Faction, index: number) => {
              const senators = publicGameState.senators
                .filter((s) => s.faction === faction.id && s.alive)
                .sort((a, b) => a.familyName.localeCompare(b.familyName))
              const myFaction = privateGameState?.faction?.id === faction.id
              const votes = senators
                .filter((s) => s.location == "Rome")
                .reduce((v, s) => v + s.votes, 0)
              return (
                <div
                  key={index}
                  className="relative rounded border border-neutral-400"
                >
                  {myFaction && (
                    <div className="absolute inset-y-[-1px] left-[-1px] w-1 bg-[#630330]" />
                  )}
                  <div className="py-0.5">
                    <div className="flex flex-wrap items-baseline gap-x-4 gap-y-2 py-2 pl-5 pr-6 text-[#630330]">
                      <h4 className="text-xl font-semibold">
                        {faction.displayName}
                      </h4>
                      <div>{faction.player.username}</div>
                      {faction.statusItems.map((status: string, i: number) => (
                        <div
                          key={i}
                          className="flex items-center rounded-full bg-neutral-200 px-2 py-0.5 text-center text-sm text-neutral-600"
                        >
                          <span className="first-letter:uppercase">
                            {status}
                          </span>
                        </div>
                      ))}
                      {(votes > 0 || faction.cardCount > 0) && (
                        <div className="ml-auto flex items-baseline gap-x-4 text-neutral-600">
                          {votes > 0 && (
                            <div>
                              <span className="text-lg tabular-nums">
                                {votes}
                              </span>{" "}
                              <span className="text-sm">
                                vote{votes !== 1 && "s"} in Rome
                              </span>
                            </div>
                          )}
                          {faction.cardCount > 0 && (
                            <div>
                              <span className="text-lg tabular-nums">
                                {faction.cardCount}
                              </span>{" "}
                              <span className="text-sm">
                                card{faction.cardCount !== 1 && "s"}
                              </span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="divide-y divide-neutral-300 border-t border-neutral-300">
                      {senators.map((senator: Senator, i: number) => (
                        <SenatorDisplay key={i} senator={senator} />
                      ))}
                    </div>
                  </div>
                </div>
              )
            })}
        </div>
      </div>

      {/* Unaligned senators + families that may return */}
      {showUnalignedSection && (
        <div className="flex flex-col gap-2">
          <div className="flex items-baseline justify-between">
            <h3 className="text-xl">Unaligned senators</h3>
            {deceasedSenators.length > 0 && (
              <Popover
                align="right"
                trigger={
                  <span className="px-2 text-sm text-neutral-600">
                    {deceasedSenators.length === 1
                      ? `${toFamilyAdjective(deceasedSenators[0].familyName)} deceased senator`
                      : `${deceasedSenators.length} deceased senators`}
                  </span>
                }
              >
                <div className="flex flex-col gap-1">
                  <span>Families that may return to politics:</span>
                  <ul className="flex flex-col gap-1">
                    {deceasedSenators.map((senator, index) => (
                      <li key={index} className="ml-6 list-disc">
                        {toFamilyAdjective(senator.familyName)} family
                      </li>
                    ))}
                  </ul>
                </div>
              </Popover>
            )}
          </div>
          {unalignedSenators.length > 0 && (
            <div className="grid grid-cols-[repeat(auto-fill,minmax(700px,1fr))] gap-4">
              <div className="rounded border border-neutral-400">
                <div className="divide-y divide-neutral-300 py-0.5">
                  {unalignedSenators.map((senator: Senator, index: number) => (
                    <SenatorDisplay key={index} senator={senator} />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Wars + enemy leaders */}
      {showConflictsSection && (
        <div className="flex flex-col gap-2">
          <div className="flex items-baseline justify-between">
            <h3 className="text-xl">Wars</h3>
            {game.militaryCrisis && (
              <span className="pr-2 text-sm text-red-600">Military crisis</span>
            )}
          </div>
          <div className="grid grid-cols-[repeat(auto-fill,minmax(400px,1fr))] gap-4">
            {publicGameState.wars
              .sort((a, b) => a.id - b.id)
              .map((war: War, index: number) => {
                const matchingWarMultiplier = war.seriesName
                  ? Math.max(
                      1,
                      publicGameState.wars.filter(
                        (w) =>
                          w.seriesName === war.seriesName &&
                          w.status === "active",
                      ).length,
                    )
                  : 1
                const leaderStrength = war.seriesName
                  ? publicGameState.enemyLeaders
                      .filter((l) => l.seriesName === war.seriesName)
                      .reduce((sum, l) => sum + l.strength, 0)
                  : 0
                const effectiveLandStrength =
                  war.landStrength * matchingWarMultiplier + leaderStrength
                const effectiveNavalStrength =
                  war.navalStrength * matchingWarMultiplier + leaderStrength
                return (
                  <div
                    key={index}
                    className="flex flex-col gap-4 rounded border border-neutral-400 px-6 py-4"
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
                            className={`flex items-center rounded-full px-2 py-0.5 text-center text-sm ${
                              (war.status === "inactive" ||
                                war.status === "defeated") &&
                              "bg-neutral-200 text-neutral-600"
                            } ${war.status === "active" && "bg-red-100 text-red-600"} ${war.status === "imminent" && "bg-amber-200 text-amber-900"}`}
                          >
                            <span className="first-letter:uppercase">
                              {war.status}
                            </span>
                          </div>
                          {war.unprosecuted && (
                            <div className="flex items-center rounded-full bg-purple-100 px-2 py-0.5 text-center text-sm text-purple-600">
                              Unprosecuted
                            </div>
                          )}
                          {war.famine && (
                            <div className="flex items-center rounded-full bg-purple-100 px-2 py-0.5 text-center text-sm text-purple-600">
                              Famine severity +1
                            </div>
                          )}
                          {war.navalStrength > 0 && (
                            <div className="flex items-center rounded-full bg-neutral-200 px-2 py-0.5 text-center text-sm text-neutral-600">
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
                    {war.seriesName && <div>Series: {war.seriesName} Wars</div>}
                    <div className="grid grid-cols-2">
                      <div className="flex flex-col gap-1">
                        <div>
                          <span className="text-sm text-neutral-600">
                            Land strength
                          </span>{" "}
                          {effectiveLandStrength}
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
                            {effectiveNavalStrength}
                          </div>
                        )}
                      </div>
                      <div className="flex flex-col gap-1">
                        <div>
                          <span className="text-sm text-neutral-600">
                            Disaster chance
                          </span>{" "}
                          {Math.round(
                            war.disasterNumbers.reduce(
                              (t, n) =>
                                t + getDiceProbability(3, 0, { exacts: [n] }),
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
                              (t, n) =>
                                t + getDiceProbability(3, 0, { exacts: [n] }),
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

            {/* Enemy leaders */}
            {publicGameState.enemyLeaders
              .sort((a, b) => a.id - b.id)
              .map((leader: EnemyLeader, index: number) => (
                <div
                  key={`leader-${index}`}
                  className="flex gap-4 rounded border border-neutral-400 px-6 py-4"
                >
                  <div className="flex grow flex-col items-start justify-between gap-4">
                    <div className="flex flex-col gap-2">
                      <h4 className="text-lg font-semibold">{leader.name}</h4>
                      <div className="flex">
                        <div
                          className={`flex items-center rounded-full px-2 py-0.5 text-center text-sm ${
                            leader.active
                              ? "bg-red-100 text-red-600"
                              : "bg-neutral-200 text-neutral-600"
                          }`}
                        >
                          {leader.active ? "Active" : "Inactive"}
                        </div>
                      </div>
                    </div>
                    <div>Series: {leader.seriesName} Wars</div>
                  </div>
                  <div className="flex flex-col gap-1">
                    <div>
                      <span className="text-sm text-neutral-600">Strength</span>{" "}
                      {leader.strength}
                    </div>
                    <div>
                      <span className="text-sm text-neutral-600">
                        Disaster chance
                      </span>{" "}
                      {Math.round(
                        getDiceProbability(3, 0, {
                          exacts: [leader.disasterNumber],
                        }) * 100,
                      )}
                      %
                    </div>
                    <div>
                      <span className="text-sm text-neutral-600">
                        Standoff chance
                      </span>{" "}
                      {Math.round(
                        getDiceProbability(3, 0, {
                          exacts: [leader.standoffNumber],
                        }) * 100,
                      )}
                      %
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Campaigns */}
      {publicGameState.campaigns.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-xl">Campaigns</h3>
          <div className="grid grid-cols-[repeat(auto-fill,minmax(400px,1fr))] gap-4">
            {publicGameState.campaigns
              .sort((a, b) => a.id - b.id)
              .map((campaign: Campaign, index: number) => {
                const war = publicGameState.wars.find(
                  (w) => w.id === campaign.war,
                )
                if (!war) return null

                const commander = publicGameState.senators.find(
                  (s) => s.id === campaign.commander,
                )
                const masterOfHorse =
                  campaign.masterOfHorse !== null
                    ? publicGameState.senators.find(
                        (s) => s.id === campaign.masterOfHorse,
                      )
                    : null
                const legions = publicGameState.legions
                  .filter((l) => l.campaign === campaign.id)
                  .sort((a, b) => a.number - b.number)
                const fleets = publicGameState.fleets
                  .filter((f) => f.campaign === campaign.id)
                  .sort((a, b) => a.number - b.number)

                let recallReason = ""
                if (!commander) {
                  recallReason = "lack of a commander"
                } else if (war.navalStrength === 0) {
                  if (legions.length === 0) {
                    recallReason = "lack of legions"
                  } else if (fleets.length < war.fleetSupport) {
                    recallReason = "insufficient fleet support"
                  }
                } else if (fleets.length === 0) {
                  recallReason = "lack of fleets"
                }

                return (
                  <div
                    key={index}
                    className="flex flex-col gap-4 rounded border border-neutral-400 px-6 py-4"
                  >
                    <div className="flex w-full items-baseline justify-between gap-4">
                      <h4 className="text-lg font-semibold">
                        {toSentenceCase(campaign.displayName)}{" "}
                        <span className="text-base font-normal text-neutral-600">
                          in {war.location}
                        </span>
                      </h4>
                      <div className="text-nowrap">{war.name}</div>
                    </div>
                    <div className="flex flex-col gap-1">
                      {masterOfHorse && (
                        <p className="text-sm">
                          Master of Horse: {masterOfHorse.displayName}
                        </p>
                      )}
                      <p>
                        {commander && (
                          <span>
                            The general{" "}
                            {masterOfHorse ? (
                              <span>
                                and his Master of Horse{" "}
                                {masterOfHorse.displayName} command{" "}
                              </span>
                            ) : (
                              <span>commands </span>
                            )}
                          </span>
                        )}
                        {legions.length > 0 && (
                          <span>
                            {legions.length}{" "}
                            {legions.length > 1 ? "legions" : "legion"}
                            <> ({forceListToString(legions)})</>
                          </span>
                        )}
                        {fleets.length > 0 && legions.length > 0 && (
                          <span> and </span>
                        )}
                        {fleets.length > 0 && (
                          <span>
                            {fleets.length}{" "}
                            {fleets.length > 1 ? "fleets" : "fleet"}
                            <> ({forceListToString(fleets)})</>
                          </span>
                        )}
                        {legions.length === 0 && fleets.length === 0 && (
                          <span>only a few loyal men</span>
                        )}
                      </p>
                      {recallReason ? (
                        <p className="text-sm text-red-600">
                          Will be automatically recalled due to {recallReason}
                        </p>
                      ) : (
                        <p className="text-sm text-neutral-600">
                          Preparing for a{" "}
                          {war.navalStrength === 0 ? "land" : "naval"} battle
                        </p>
                      )}
                    </div>
                  </div>
                )
              })}
          </div>
        </div>
      )}
    </div>
  )
}

export default GameMain
