import { Component } from 'react';
import axios from "axios";

class SignInForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password: '',
      feedback: '',
      submit: <input className="submit submit-ready" type="submit" value="Submit" />
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
    this.setState({
      submit: <div className="submit submit-loading"><img src={require("../images/throbber_light.gif")} alt="loading" /></div>
    });

    event.preventDefault();
    this.feedBack = null;

    const username = this.state.username;
    const password = this.state.password;

    if (username === '' || password === '') {
      this.setState({
        feedback: <div class="feedback">Please provide a username and a password</div>
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
          feedback: <div class="feedback">Your username and password do not match. Please try again.</div>
        });
      });
    }

    this.setState({
      submit: <input className="submit submit-ready" type="submit" value="Submit" />
    });
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="form">
        {this.state.feedback}
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
          {this.state.submit}
        </div>
      </form>
    );
  }
}

export default SignInForm;