class Game {
  name: String;
  owner: String | null;
  description: String | null;
  creationDate: Date | null;
  startDate: Date | null;

  constructor(
    name: String,
    owner: String | null,
    description: String | null,
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