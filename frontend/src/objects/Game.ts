class Game {
  name: string;
  owner: string | null;
  description: string | null;
  creationDate: Date | null;
  startDate: Date | null;

  constructor(
    name: string,
    owner: string | null,
    description: string | null,
    creationDate: string | null,
    startDate: string | null
    ) {
      this.name = name;
      this.owner = owner;
      this.description = description;
      this.creationDate = creationDate !== null ? new Date(creationDate) : null;
      this.startDate = startDate !== null ? new Date(startDate) : null;
    }
}

export default Game;