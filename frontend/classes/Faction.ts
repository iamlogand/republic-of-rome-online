export interface FactionData {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  card_count: number
  status_items: string[]
}

class Faction {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  card_count: number
  status_items: string[]

  constructor(data: FactionData) {
    this.id = data.id
    this.player = data.player
    this.position = data.position
    this.card_count = data.card_count
    this.status_items = data.status_items
  }
}

export default Faction
