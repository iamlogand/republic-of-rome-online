interface TurnData {
  id: number
  index: number
  game: number
}

class Turn {
  id: number
  index: number
  game: number

  constructor(data: TurnData) {
    this.id = data.id
    this.index = data.index
    this.game = data.game
  }
}

export default Turn
