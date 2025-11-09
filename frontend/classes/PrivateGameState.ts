import AvailableAction, { AvailableActionData } from "./AvailableAction"
import PrivateFaction, { PrivateFactionData } from "./PrivateFaction"

export interface PrivateGameStateData {
  available_actions: AvailableActionData[]
  faction: PrivateFactionData | undefined
}

class PrivateGameState {
  availableActions: AvailableAction[]
  faction: PrivateFaction | undefined

  constructor(data: PrivateGameStateData) {
    this.availableActions = data.available_actions
    this.faction = data.faction ? new PrivateFaction(data.faction) : undefined
  }
}

export default PrivateGameState
