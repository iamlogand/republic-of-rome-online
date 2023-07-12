interface FactionData {
  id: string,
  game: string,
  position: string,
  player: string
}

class Faction {
  id: string;
  game: string;
  position: string;
  player: string;

  constructor(data: FactionData) {
    this.id = data.id;
    this.game = data.game;
    this.position = data.position;
    this.player = data.player;
  }
}

export default Faction
