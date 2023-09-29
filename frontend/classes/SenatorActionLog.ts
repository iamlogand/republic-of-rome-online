interface SenatorActionLogData {
  id: number
  senator: number
  action_log: number
}

class SenatorActionLog {
  id: number
  senator: number
  action_log: number

  constructor(data: SenatorActionLogData) {
    this.id = data.id
    this.senator = data.senator
    this.action_log = data.action_log
  }
}

export default SenatorActionLog
