export type FactionPosition = "0" | "1" | "2" | "3" | "4" | "5" | "6"

interface FactionData {
  id: string,
  game: string,
  position: FactionPosition,
  player: string
}

class Faction {
  id: string
  game: string
  position: FactionPosition
  player: string

  constructor(data: FactionData) {
    this.id = data.id
    this.game = data.game
    this.position = data.position
    this.player = data.player
  }
}

export default Faction
