interface UserData {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
}

class User {
  id: number
  username: string
  firstName: string
  lastName: string
  email: string

  constructor(data: UserData) {
    this.id = data.id
    this.username = data.username
    this.firstName = data.first_name
    this.lastName = data.last_name
    this.email = data.email
  }
}

export default User
