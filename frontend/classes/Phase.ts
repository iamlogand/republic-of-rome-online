interface PhaseData {
  id: number
  name: string
  turn: number
}

class Phase {
  id: number
  name: string
  turn: number

  constructor(data: PhaseData) {
    this.id = data.id
    this.name = data.name
    this.turn = data.turn
  }
}

export default Phase
