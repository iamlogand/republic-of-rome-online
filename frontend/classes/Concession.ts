interface ConcessionData {
  id: number
  name: string
  game: number
  senator: number
}

class Concession {
  id: number
  name: string
  game: number
  senator: number

  constructor(data: ConcessionData) {
    this.id = data.id
    this.name = data.name
    this.game = data.game
    this.senator = data.senator
  }
}

export default Concession
