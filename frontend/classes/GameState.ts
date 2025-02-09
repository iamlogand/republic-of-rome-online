import Faction, { FactionData } from "./Faction"
import Game, { GameData } from "./Game"
import Senator, { SenatorData } from "./Senator"

export interface GameStateData {
  timestamp: string
  factions: FactionData[]
  game: GameData | undefined
  senators: SenatorData[]
}

class GameState {
  timestamp: string
  factions: Faction[]
  game: Game | undefined
  senators: Senator[]

  constructor(data: GameStateData) {
    this.timestamp = data.timestamp
    this.factions = data.factions
      ? data.factions.map(
          (factionData: FactionData) => new Faction(factionData)
        )
      : []
    this.game = data.game ? new Game(data.game) : undefined
    this.senators = data.senators
      ? data.senators.map(
          (senatorData: SenatorData) => new Senator(senatorData)
        )
      : []
  }
}

export default GameState
