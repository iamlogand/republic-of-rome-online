import Faction, { FactionData } from "./Faction"
import Game, { GameData } from "./Game"

export interface GameStateData {
  timestamp: string
  factions: FactionData[]
  game: GameData | undefined
}

class GameState {
  timestamp: string
  factions: Faction[]
  game: Game | undefined

  constructor(data: GameStateData) {
    this.timestamp = data.timestamp
    this.factions = data.factions
      ? data.factions.map(
          (factionData: FactionData) => new Faction(factionData)
        )
      : []
    this.game = data.game ? new Game(data.game) : undefined
  }
}

export default GameState
