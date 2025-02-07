export interface GameData {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  created_on: string
}

class Game {
  id: number
  name: string
  host: {
    id: number
    username: string
  }
  createdOn: string

  constructor(
    id: number,
    name: string,
    host: {
      id: number
      username: string
    },
    createdOn: string
  ) {
    this.id = id
    this.name = name
    this.host = host
    this.createdOn = createdOn
  }
}

export default Game
