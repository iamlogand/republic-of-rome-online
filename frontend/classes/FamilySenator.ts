class FamilySenator {
  id: string;
  name: string;
  game: string;
  faction: string;

  constructor(
    id: string,
    name: string,
    game: string,
    faction: string
  ) {
    this.id = id;
    this.name = name;
    this.game = game;
    this.faction = faction;
  }
}

export default FamilySenator
