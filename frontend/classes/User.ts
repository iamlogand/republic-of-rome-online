interface IUser {
  id: number;
  username: string;
  email: string;
}

class User {
  id: number;
  username: string;
  email: string;

  constructor(data: IUser) {
    this.id = data.id;
    this.username = data.username;
    this.email = data.email;
  }
}

export default User
