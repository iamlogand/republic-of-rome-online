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
      <h3 className="text-xl mt-4">Sequence of play</h3>
      <div className="flex gap-4">
        <div>Turn: {publicGameState.game?.turn}</div>
        <div>
          Phase: <span>{publicGameState.game?.phase}</span>
        </div>
        <div>
          {publicGameState.game?.subPhase && (
            <span className="text-neutral-500">
              {" "}
              Sub-phase: {publicGameState.game?.subPhase}
            </span>
          )}
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

          return (
            <div
              key={index}
              className="py-0.5 border border-neutral-400 rounded"
            >
              <h4 className="px-4 py-1 flex gap-4">
                <div>{faction.displayName}</div>
                <div>{faction.player.username}</div>
                {faction.statusItems.length > 0 &&
                  faction.statusItems.map((status: string, index: number) => (
                    <div key={index} className="text-neutral-500">{status}</div>
                  ))}
              </h4>
              <div>
                {senators.map((senator: Senator, index: number) => (
                  <div key={index}>
                    <hr className="border-neutral-300" />
                    <div className="flex px-4 py-1 gap-x-8 gap-y-1 flex-wrap">
                      <div className="w-[140px]">
                        <p className="">
                          {senator.displayName}{" "}
                          <span className="text-neutral-500">
                            [{senator.code}]
                          </span>
                        </p>
                      </div>
                      <div className="flex gap-x-4 gap-y-1 flex-wrap">
                        <div>
                          <span className="text-neutral-500">Military</span>{" "}
                          <span className="inline-block w-[15px]">
                            {senator.military}
                          </span>
                        </div>
                        <div>
                          <span className="text-neutral-500">Oratory</span>{" "}
                          <span className="inline-block w-[15px]">
                            {senator.military}
                          </span>
                        </div>
                        <div>
                          <span className="text-neutral-500">Loyalty</span>{" "}
                          <span className="inline-block w-[15px]">
                            {senator.military}
                          </span>
                        </div>
                        <div>
                          <span className="text-neutral-500">Influence</span>{" "}
                          <span className="inline-block w-[15px]">
                            {senator.influence}
                          </span>
                        </div>
                        <div>
                          <span className="text-neutral-500">Popularity</span>{" "}
                          <span className="inline-block w-[15px]">
                            {senator.popularity}
                          </span>
                        </div>
                        <div>
                          <span className="text-neutral-500">Knights</span>{" "}
                          <span className="inline-block w-[15px]">
                            {senator.knights}
                          </span>
                        </div>
                        <div>
                          <span className="text-neutral-500">Votes</span>{" "}
                          <span className="inline-block w-[15px]">
                            {senator.votes}
                          </span>
                        </div>
                        <div>
                          <span className="text-neutral-500">Talents</span>{" "}
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
                              <div key={index} className="text-neutral-500">{status}</div>
                            ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      <h3 className="text-xl mt-4">Logs</h3>
      <div className="border border-neutral-400 rounded overflow-hidden">
        <div className="max-h-[200px] overflow-auto px-4 py-1 flex flex-col-reverse gap-1">
          {publicGameState?.logs &&
            publicGameState.logs
              .sort((a, b) => compareDates(b.createdOn, a.createdOn))
              .map((log: Log, index: number) => {
                return (
                  <div key={index} className="flex gap-x-4 flex-wrap">
                    <div className="text-neutral-500 min-w-[210px]">
                      {formatDate(log.createdOn)}
                    </div>
                    <div>{log.text}</div>
                  </div>
                )
              })}
        </div>
      </div>
      {privateGameState?.faction && (
        <>
          <h3 className="text-xl mt-4">Your faction</h3>
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
          <div className="flex flex-col gap-4">
            <p>Available actions:</p>
            <div className="flex gap-4">
              {privateGameState?.availableActions.length > 0
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
        </>
      )}
    </div>
  )
}

export default GameContainer
