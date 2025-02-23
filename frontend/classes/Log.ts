export interface LogData {
  id: number
  turn: number
  phase: string
  created_on: string
  text: string
}

class Log {
  id: number
  turn: number
  phase: string
  createdOn: string
  text: string

  constructor(data: LogData) {
    this.id = data.id
    this.turn = data.turn
    this.phase = data.phase
    this.createdOn = data.created_on
    this.text = data.text
  }
}

export default Log
