export interface CampaignData {
  id: number
  game: number
  commander: number
  master_of_horse: number | null
  war: number | null
  land_victory: boolean
  display_name: string
}

class Campaign {
  id: number
  game: number
  commander: number
  masterOfHorse: number | null
  war: number | null
  landVictory: boolean
  displayName: string

  constructor(data: CampaignData) {
    this.id = data.id
    this.game = data.game
    this.commander = data.commander
    this.masterOfHorse = data.master_of_horse
    this.war = data.war
    this.landVictory = data.land_victory
    this.displayName = data.display_name
  }
}

export default Campaign
