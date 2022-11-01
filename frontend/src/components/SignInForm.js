import { Component } from 'react';
import axios from "axios";
import "./SignInForm.css";

class SignInForm extends Component {
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

    const name = this.state.username

    const data = JSON.stringify({
      "username": name,
      "password": this.state.password
    });

    axios.post(process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/', data, {
      headers: { "Content-Type": "application/json" }
    }).then(response => {
      this.props.setAuthData(name, response.data.access);
    }).catch(error => {
      console.log(error);
      this.setState({password: ''});
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="form">
        <div className="field">
          <label htmlFor="username">Username </label>
          <input
            type="text"
            id="username"
            name="username"
            autoComplete="username"
            value={this.state.username}
            onChange={this.handleInputChange} />
        </div>
        <div className="field">
          <label htmlFor="password">Password </label>
          <input
            type="password"
            id="password"
            name="password"
            autoComplete="current-password"
            value={this.state.password}
            onChange={this.handleInputChange} />
        </div>
        <div>
          <input className="submit" type="submit" value="Submit" />
        </div>
      </form>
    );
  }
}

export default SignInForm;