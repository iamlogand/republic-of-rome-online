export interface PrivateFactionData {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  treasury: number
  cards: string[]
  card_count: number
  status_items: string[]
  display_name: string
}

class PrivateFaction {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
  treasury: number
  cards: string[]
  cardCount: number
  statusItems: string[]
  displayName: string

  constructor(data: PrivateFactionData) {
    this.id = data.id
    this.player = data.player
    this.position = data.position
    this.treasury = data.treasury
    this.cards = data.cards
    this.cardCount = data.card_count
    this.statusItems = data.status_items
    this.displayName = data.display_name
  }
}

export default PrivateFaction
