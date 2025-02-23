import Faction, { FactionData } from "./Faction"
import Game, { GameData } from "./Game"
import Log, { LogData } from "./Log"
import Senator, { SenatorData } from "./Senator"

export interface PublicGameStateData {
  timestamp: string
  factions: FactionData[]
  game: GameData | undefined
  senators: SenatorData[]
  logs: LogData[]
}

class PublicGameState {
  timestamp: string
  factions: Faction[]
  game: Game | undefined
  senators: Senator[]
  logs: Log[]

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
    this.logs = data.logs
      ? data.logs.map((logData: LogData) => new Log(logData))
      : []
  }
}

export default PublicGameState
