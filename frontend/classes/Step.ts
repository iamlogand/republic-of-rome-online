interface StepData {
  id: number
  index: number
  phase: number
}

class Step {
  id: number
  index: number
  phase: number

  constructor(data: StepData) {
    this.id = data.id
    this.index = data.index
    this.phase = data.phase
  }
}

export default Step
