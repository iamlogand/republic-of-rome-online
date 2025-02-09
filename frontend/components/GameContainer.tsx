"use client"

import Faction from "@/classes/Faction"
import GameState from "@/classes/GameState"
import Senator from "@/classes/Senator"

interface GameContainerProps {
  gameState: GameState
}

const GameContainer = ({ gameState }: GameContainerProps) => {
  return (
    <div className="px-6 py-4 flex flex-col gap-4">
      <h3 className="text-xl">Factions</h3>
      {gameState.factions
        .sort((a, b) => a.position - b.position)
        .map((faction: Faction, index: number) => {
          const senators = gameState.senators
            .filter((s) => s.faction === faction.id && s.alive)
            .sort((a, b) => a.name.localeCompare(b.name))

          return (
            <div key={index} className="border border-neutral-300 rounded">
              <h4 className="px-2">Faction {faction.position}</h4>
              <div>
                {senators.map((senator: Senator, index: number) => (
                  <>
                    <hr className="border-neutral-300" />
                    <div key={index} className="flex px-2">
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
                      </div>
                    </div>
                  </>
                ))}
              </div>
            </div>
          )
        })}
    </div>
  )
}

export default GameContainer
