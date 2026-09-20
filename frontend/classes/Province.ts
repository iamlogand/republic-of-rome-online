export interface ProvinceData {
  id: number
  game: number
  name: string
  developed: boolean
  frontier: boolean
  governor: number | null
  term: number | null
}

class Province {
  id: number
  game: number
  name: string
  developed: boolean
  frontier: boolean
  governor: number | null
  term: number | null

  constructor(data: ProvinceData) {
    this.id = data.id
    this.game = data.game
    this.name = data.name
    this.developed = data.developed
    this.frontier = data.frontier
    this.governor = data.governor
    this.term = data.term
  }
}

export default Province