class Faction {
  id: string;
  game: string;
  position: string;
  player: string;

  constructor(
    id: string,
    game: string,
    position: string,
    player: string
  ) {
    this.id = id;
    this.game = game;
    this.position = position;
    this.player = player;
  }
}

export default Faction
