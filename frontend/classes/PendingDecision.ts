export interface PendingDecisionData {
  faction: number
  description: string
}

class PendingDecision {
  factionId: number
  description: string

  constructor(data: PendingDecisionData) {
    this.factionId = data.faction
    this.description = data.description
  }
}

export default PendingDecision
