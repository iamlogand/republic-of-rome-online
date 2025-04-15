import Faction, { FactionData } from "./Faction"
import Game, { GameData } from "./Game"
import Log, { LogData } from "./Log"
import Senator, { SenatorData } from "./Senator"
import War, { WarData } from "./War"

export interface PublicGameStateData {
  timestamp: string
  factions: FactionData[]
  game: GameData | undefined
  senators: SenatorData[]
  logs: LogData[]
  wars: WarData[]
}

class PublicGameState {
  timestamp: string
  factions: Faction[]
  game: Game | undefined
  senators: Senator[]
  logs: Log[]
  wars: War[]

  constructor(data: PublicGameStateData) {
    this.timestamp = data.timestamp
    this.factions = data.factions
      ? data.factions.map(
          (factionData: FactionData) => new Faction(factionData),
        )
      : []
    this.game = data.game ? new Game(data.game) : undefined
    this.senators = data.senators
      ? data.senators.map(
          (senatorData: SenatorData) => new Senator(senatorData),
        )
      : []
    this.logs = data.logs
      ? data.logs.map((logData: LogData) => new Log(logData))
      : []
    this.wars = data.wars
      ? data.wars.map((warData: WarData) => new War(warData))
      : []
  }
}

export default PublicGameState
