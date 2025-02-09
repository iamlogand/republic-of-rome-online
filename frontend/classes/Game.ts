export interface GameData {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  created_on: string
  factions?: [
    {
      player: {
        id: number
        username: string
      }
    }
  ]
}

class Game {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  createdOn: string
  factions?: [
    {
      player: {
        id: number
        username: string
      }
    }
  ]

  constructor(data: GameData) {
    this.id = data.id
    this.name = data.name
    this.host = data.host
    this.createdOn = data.created_on
    this.factions = data.factions
  }
}

export default Game
