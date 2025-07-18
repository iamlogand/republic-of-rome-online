import Campaign, { CampaignData } from "./Campaign"
import Faction, { FactionData } from "./Faction"
import Fleet, { FleetData } from "./Fleet"
import Game, { GameData } from "./Game"
import Legion, { LegionData } from "./Legion"
import Log, { LogData } from "./Log"
import Senator, { SenatorData } from "./Senator"
import War, { WarData } from "./War"

export interface PublicGameStateData {
  timestamp: string
  campaigns: CampaignData[]
  factions: FactionData[]
  fleets: Fleet[]
  game: GameData | undefined
  legions: Legion[]
  logs: LogData[]
  senators: SenatorData[]
  wars: WarData[]
}

class PublicGameState {
  timestamp: string
  campaigns: Campaign[]
  factions: Faction[]
  fleets: Fleet[]
  game: Game | undefined
  legions: Legion[]
  logs: Log[]
  senators: Senator[]
  wars: War[]

  constructor(data: PublicGameStateData) {
    this.timestamp = data.timestamp

    this.campaigns = data.campaigns
      ? data.campaigns.map(
          (campaignData: CampaignData) => new Campaign(campaignData),
        )
      : []
    this.factions = data.factions
      ? data.factions.map(
          (factionData: FactionData) => new Faction(factionData),
        )
      : []
    this.fleets = data.fleets
      ? data.fleets.map((fleetData: FleetData) => new Fleet(fleetData))
      : []
    this.game = data.game ? new Game(data.game) : undefined
    this.legions = data.legions
      ? data.legions.map((legionData: LegionData) => new Legion(legionData))
      : []
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
