class Game {
  name: String;
  owner: String;
  description: String;
  creationDate: Date | null;
  startDate: Date | null;

  constructor(
    name: String,
    owner: String,
    description: String,
    creationDate: Date | null,
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