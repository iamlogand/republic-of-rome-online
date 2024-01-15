interface SecretData {
  id: number
  name: string | null
  type: string | null
  faction: number
}

class Secret {
  public id: number
  public name: string | null
  public type: string | null
  public faction: number

  constructor(data: SecretData) {
    this.id = data.id
    this.name = data.name
    this.type = data.type
    this.faction = data.faction
  }
}

export default Secret
