"use client"

import AvailableAction from "@/classes/AvailableAction"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import ActionHandler from "./ActionHandler"

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
          Phase:{" "}
          <span className="capitalize">{publicGameState.game?.phase}</span>
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
                <div>Faction {faction.position}</div>
                <div>{faction.player.username}</div>
                {faction.status.length > 0 &&
                  faction.status.map((status: string, index: number) => (
                    <div key={index}>{status}</div>
                  ))}
              </h4>
              <div>
                {senators.map((senator: Senator, index: number) => (
                  <div key={index}>
                    <hr className="border-neutral-300" />
                    <div className="flex px-4 py-1 gap-x-4 gap-y-1 flex-wrap">
                      <div className="w-[140px]">
                        <p className="">
                          {senator.name}{" "}
                          <span className="text-neutral-600">
                            [{senator.code}]
                          </span>
                        </p>
                      </div>
                      <div className="flex gap-x-4 gap-y-1 flex-wrap">
                        <div>
                          <span className="text-neutral-600">Military</span>{" "}
                          {senator.military}
                        </div>
                        <div>
                          <span className="text-neutral-600">Oratory</span>{" "}
                          {senator.military}
                        </div>
                        <div>
                          <span className="text-neutral-600">Loyalty</span>{" "}
                          {senator.military}
                        </div>
                        <div>
                          <span className="text-neutral-600">Influence</span>{" "}
                          {senator.influence}
                        </div>
                        <div>
                          <span className="text-neutral-600">Popularity</span>{" "}
                          {senator.popularity}
                        </div>
                        <div>
                          <span className="text-neutral-600">Knights</span>{" "}
                          {senator.knights}
                        </div>
                        <div>
                          <span className="text-neutral-600">Votes</span>{" "}
                          {senator.votes}
                        </div>
                        <div>
                          <span className="text-neutral-600">Talents</span>{" "}
                          {senator.talents}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
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
