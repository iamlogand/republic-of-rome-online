interface SenatorData {
  id: number,
  name: string,
  game: number,
  faction: number
}

class Senator {
  id: number;
  name: string;
  game: number;
  faction: number;

  constructor(data: SenatorData) {
    this.id = data.id;
    this.name = data.name;
    this.game = data.game;
    this.faction = data.faction;
  }
}

export default Senator
