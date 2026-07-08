export interface ProvinceData {
  id: number
  game: number
  name: string
  developed: boolean
  frontier: boolean
}

class Province {
  id: number
  game: number
  name: string
  developed: boolean
  frontier: boolean

  constructor(data: ProvinceData) {
    this.id = data.id
    this.game = data.game
    this.name = data.name
    this.developed = data.developed
    this.frontier = data.frontier
  }
}

export default Province