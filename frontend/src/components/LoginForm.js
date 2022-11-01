import { Component } from 'react';
import axios from "axios";

class LoginForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: ''
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    if (event.target.name === 'username') {
      this.setState({ username: event.target.value });
    } else if (event.target.name === "password") {
      this.setState({ password: event.target.value });
    }
  }

  handleSubmit(event) {
    event.preventDefault();

    const data = JSON.stringify({
      "username": this.state.username,
      "password": this.state.password
    });

    axios.post(process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/', data, {
      headers: { "Content-Type": "application/json" }
    }).then(response => {
      console.log(response.data.access);
      this.props.setAccessToken(response.data.access);
    }).catch(error => {
      console.log(error)
    });
  }

  render() {
    return (
      <div>
        <h3>Please Login</h3>
        <form onSubmit={this.handleSubmit}>
          <div>
            <label htmlFor="username">Username </label>
            <input
              type="text"
              id="username"
              name="username"
              value={this.state.username}
              onChange={this.handleInputChange} />
          </div>
          <div>
            <label htmlFor="password">Password </label>
            <input
              type="password"
              id="password"
              name="password"
              value={this.state.password}
              onChange={this.handleInputChange} />
          </div>
          <div>
            <input type="submit" value="Submit" />
          </div>
        </form>
      </div>
    );
  }
}

export default LoginForm;