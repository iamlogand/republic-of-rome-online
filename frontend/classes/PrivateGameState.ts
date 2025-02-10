import AvailableAction, { AvailableActionData } from "./AvailableActions"
import PrivateFaction, { PrivateFactionData } from "./PrivateFaction"

export interface PrivateGameStateData {
  timestamp: string
  available_actions: AvailableActionData[]
  faction: PrivateFactionData | undefined
}

class PrivateGameState {
  timestamp: string
  availableActions: AvailableAction[]
  faction: PrivateFaction | undefined

  constructor(data: PrivateGameStateData) {
    this.timestamp = data.timestamp
    this.availableActions = data.available_actions
    this.faction = data.faction ? new PrivateFaction(data.faction) : undefined
  }
}

export default PrivateGameState
