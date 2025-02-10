export interface AvailableActionData {
  id: number
  game: number
  faction: number
  type: string
  schema: number
}

class AvailableAction {
  id: number
  game: number
  faction: number
  type: string
  schema: number

  constructor(data: AvailableActionData) {
    this.id = data.id
    this.game = data.game
    this.faction = data.faction
    this.type = data.type
    this.schema = data.schema
  }
}

export default AvailableAction
