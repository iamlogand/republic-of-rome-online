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
    creationDate: string,
    startDate: string | null
    ) {
      this.name = name;
      this.owner = owner;
      this.description = description;
      this.creationDate = new Date(creationDate);
      this.startDate = startDate !== null ? new Date(startDate) : null;
    }
}

export default Game;