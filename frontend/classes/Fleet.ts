export interface FleetData {
  id: number
  game: number
  number: number
  name: string
}

class Fleet {
  id: number
  game: number
  number: number
  name: string

  constructor(data: FleetData) {
    this.id = data.id
    this.game = data.game
    this.number = data.number
    this.name = data.name
  }
}

export default Fleet
