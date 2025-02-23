export interface LogData {
  id: number
  created_on: string
  text: string
}

class Log {
  id: number
  createdOn: string
  text: string

  constructor(data: LogData) {
    this.id = data.id
    this.createdOn = data.created_on
    this.text = data.text
  }
}

export default Log
