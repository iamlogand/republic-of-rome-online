"use client"

import AvailableAction from "@/classes/AvailableActions"
import Faction from "@/classes/Faction"
import PrivateGameState from "@/classes/PrivateGameState"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"

interface GameContainerProps {
  publicGameState: PublicGameState
  privateGameState: PrivateGameState | undefined
}

const GameContainer = ({
  publicGameState,
  privateGameState,
}: GameContainerProps) => {
  return (
    <div className="px-6 py-4 flex flex-col gap-4">
      <h3 className="text-xl mt-4">Sequence of play</h3>
      <div className="flex gap-4">
        <div>Turn: {publicGameState.game?.turn}</div>
        <div>Phase: <span className="capitalize">{publicGameState.game?.phase}</span></div>
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
                <div>Faction {faction.position}</div>{" "}
                <div>{faction.player.username}</div>
              </h4>
              <div>
                {senators.map((senator: Senator, index: number) => (
                  <div key={index}>
                    <hr className="border-neutral-300" />
                    <div className="flex px-4 py-1">
                      <div className="w-[140px]">
                        <p className="">
                          {senator.name}{" "}
                          <span className="text-neutral-600">
                            [{senator.code}]
                          </span>
                        </p>
                      </div>
                      <div className="flex gap-3">
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
          <div>
            Available actions:{" "}
            {privateGameState?.availableActions.length > 0
              ? privateGameState?.availableActions.map(
                  (action: AvailableAction, index: number) => (
                    <span key={index}>
                      <span className="capitalize">{action.name}</span>
                      {index <
                        privateGameState?.availableActions.length - 1 && (
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
