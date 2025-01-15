class User {
  id: number
  username: string
  firstName: string
  lastName: string
  email: string

  constructor(
    id: number,
    username: string,
    first_name: string,
    last_name: string,
    email: string
  ) {
    this.id = id
    this.username = username
    this.firstName = first_name
    this.lastName = last_name
    this.email = email
  }
}

export default User
