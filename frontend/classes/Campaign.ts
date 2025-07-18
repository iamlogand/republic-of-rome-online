export interface CampaignData {
  id: number
  game: number
  commander: number
  master_of_horse: number | null
  war: number
}

class Campaign {
  id: number
  game: number
  commander: number
  masterOfHorse: number | null
  war: number

  constructor(data: CampaignData) {
    this.id = data.id
    this.game = data.game
    this.commander = data.commander
    this.masterOfHorse = data.master_of_horse
    this.war = data.war
  }
}

export default Campaign
