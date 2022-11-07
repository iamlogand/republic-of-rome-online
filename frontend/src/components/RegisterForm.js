import { Component } from 'react';
import axios from "axios";

class RegisterForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: '',
      password1: '',
      feedback: '',
      submitReady: true
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    if (event.target.name === 'username') {
      this.setState({ username: event.target.value });
    } else if (event.target.name === "password1") {
      this.setState({ password1: event.target.value });
    }
  }

  handleSubmit(event) {
    event.preventDefault();

    this.setState({
      submitReady: false
    });

    this.feedBack = null;

    const username = this.state.username;
    const password1 = this.state.password1;

    if (username === '' || password1 === '') {
      this.setState({
        feedback: 'Please provide a username and a password.',
        submitReady: true
      });
    } else {

      const data = JSON.stringify({
        "username": username,
        "password1": password1
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
        if (error.code === "ERR_BAD_REQUEST") {
          this.setState({
            password1: '',
            feedback: 'Your username and password do not match. Please try again.',
            submitReady: true
          });
        } else {
          this.setState({
            password1: '',
            feedback: 'Something went wrong. Please try again later.',
            submitReady: true
          });
        }
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
          <label htmlFor="username">Username</label>
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
          <label htmlFor="password1">Password</label>
          <input
            type="password"
            id="password1"
            name="password1"
            autoComplete="new-password"
            className="field_input"
            value={this.state.password1}
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

export default RegisterForm;