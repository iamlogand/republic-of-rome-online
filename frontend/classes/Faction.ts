export interface FactionData {
  id: number
  player: {
    id: number
    username: string
  }
  position: number
}

class Faction {
  id: number
  player: {
    id: number
    username: string
  }
  position: number

  constructor(data: FactionData) {
    this.id = data.id
    this.player = data.player
    this.position = data.position
  }
}

export default Faction
