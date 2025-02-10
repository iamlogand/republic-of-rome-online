import Faction, { FactionData } from "./Faction"
import Game, { GameData } from "./Game"
import Senator, { SenatorData } from "./Senator"

export interface PublicGameStateData {
  timestamp: string
  factions: FactionData[]
  game: GameData | undefined
  senators: SenatorData[]
}

class PublicGameState {
  timestamp: string
  factions: Faction[]
  game: Game | undefined
  senators: Senator[]

  constructor(data: PublicGameStateData) {
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

export default PublicGameState
