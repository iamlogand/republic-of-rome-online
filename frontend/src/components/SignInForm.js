import { Component } from 'react';
import axios from "axios";

class SignInForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      feedback: '',
      submitReady: true
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

    this.setState({
      submitReady: false
    });

    this.feedBack = null;

    const username = this.state.username;
    const password = this.state.password;

    if (username === '' || password === '') {
      this.setState({
        feedback: 'Please provide a username and a password.',
        submitReady: true
      });
    } else {

      const data = JSON.stringify({
        "username": username,
        "password": password
      });

      axios.post(process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/', data, {
        headers: { "Content-Type": "application/json" }
      }).then(response => {
        this.props.setAuthData({
          accessToken: response.data.access,
          refreshToken: response.data.refresh,
          username: username
        });
      }).catch(error => {
        console.log(error);
        this.setState({
          password: '',
          feedback: 'Your username and password do not match. Please try again.',
          submitReady: true
        });
      });
    }
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="form">
        {this.state.feedback !== '' &&
          <div class="feedback">{this.state.feedback}</div>
        }
        <div className="field">
          <label htmlFor="username">Username </label>
          <input
            type="text"
            id="username"
            name="username"
            autoComplete="username"
            className="field_input"
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
            className="field_input"
            value={this.state.password}
            onChange={this.handleInputChange} />
        </div>
        <div>
          {this.state.submitReady === true
          ? <input className="submit submit-ready" type="submit" value="Submit" />
          : <div className="submit submit-loading"><img src={require("../images/throbber_light.gif")} alt="loading" /></div>
          }
        </div>
      </form>
    );
  }
}

export default SignInForm;