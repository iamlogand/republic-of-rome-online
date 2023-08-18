interface PhaseData {
  id: number
  name: string
  index: number
  turn: number
}

class Phase {
  id: number
  name: string
  index: number
  turn: number

  constructor(data: PhaseData) {
    this.id = data.id
    this.name = data.name
    this.index = data.index
    this.turn = data.turn
  }
}

export default Phase
