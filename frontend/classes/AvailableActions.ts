export interface AvailableActionData {
  id: number
  game: number
  faction: number
  name: string
  schema: number
}

class AvailableAction {
  id: number
  game: number
  faction: number
  name: string
  schema: number

  constructor(data: AvailableActionData) {
    this.id = data.id
    this.game = data.game
    this.faction = data.faction
    this.name = data.name
    this.schema = data.schema
  }
}

export default AvailableAction
