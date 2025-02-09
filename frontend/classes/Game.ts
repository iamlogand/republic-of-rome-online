export interface GameData {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  created_on: string
  started_on?: string
  finished_on?: string
  factions?: [
    {
      player: {
        id: number
        username: string
      }
    }
  ]
  status: string
}

class Game {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  createdOn: string
  startedOn?: string
  finishedOn?: string
  factions?: [
    {
      player: {
        id: number
        username: string
      }
    }
  ]
  status: string

  constructor(data: GameData) {
    this.id = data.id
    this.name = data.name
    this.host = data.host
    this.createdOn = data.created_on
    this.startedOn = data.started_on
    this.finishedOn = data.finished_on
    this.factions = data.factions
    this.status = data.status
  }
}

export default Game
