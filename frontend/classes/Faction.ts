export interface FactionData {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  card_count: number
  status_items: string[]
  display_name: string
}

class Faction {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  cardCount: number
  statusItems: string[]
  displayName: string

  constructor(data: FactionData) {
    this.id = data.id
    this.player = data.player
    this.position = data.position
    this.cardCount = data.card_count
    this.statusItems = data.status_items
    this.displayName = data.display_name
  }
}

export default Faction
