class GameParticipant {
  id: string;
  user: string;
  game: string;
  joinDate: Date;

  constructor(
    id: string,
    user: string,
    game: string,
    joinDate: string
  ) {
    this.id = id;
    this.user = user;
    this.game = game;
    this.joinDate = new Date(joinDate);
  }
}

export default GameParticipant
