class Game {
  name: string;
  owner: string | null;
  description: string | null;
  creationDate: Date;
  startDate: Date | null;

  constructor(
    name: string,
    owner: string | null,
    description: string | null,
    creationDate: Date,
    startDate: Date | null
  ) {
    this.name = name;
    this.owner = owner;
    this.description = description;
    this.creationDate = creationDate;
    this.startDate = startDate;
  }
}

export default Game;
