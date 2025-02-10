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
  card_count: number

  constructor(data: PrivateFactionData) {
    this.id = data.id
    this.player = data.player
    this.position = data.position
    this.treasury = data.treasury
    this.cards = data.cards
    this.card_count = data.card_count
  }
}

export default PrivateFaction
