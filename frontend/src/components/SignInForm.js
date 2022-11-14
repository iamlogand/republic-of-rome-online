import { Component } from 'react';
import axios from "axios";

class SignInForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      identity: '',
      password: '',
      feedback: '',
      identityError: false,
      passwordError: false,
      pending: false,
      feedbackFlash: false,
      submitReady: true
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    if (event.target.name === 'identity') {
      this.setState({ identity: event.target.value });
    } else if (event.target.name === "password") {
      this.setState({ password: event.target.value });
    }
  }

  handleSubmit(event) {
    event.preventDefault();

    this.setState({
      feedbackFlash: true
    });

    setTimeout(async () => {
      const identity = this.state.identity;
      const password = this.state.password;

      if (identity === '' && password === '') {
        this.setState({
          feedback: 'Please enter your username or email and password',
          identityError: true,
          passwordError: true
        });
        return;

      } else if (identity === '') {
        this.setState({
          feedback: 'Please enter your username or email',
          identityError: true,
          passwordError: false
        });
        return;
        
      } else if (password === '') {
        this.setState({
          feedback: 'Please enter your password',
          identityError: false,
          passwordError: true
        });
        return;
      }

      this.setState({
        pending: true,
        submitReady: false,
      });

      let response;
      let username;
      let result;

      try {
        response = await axios({
          method: 'post',
          url: process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/',
          headers: { "Content-Type": "application/json" },
          data: JSON.stringify({ "username": identity, "password": password })
        });
        result = 'success';
      } catch (error) {

        console.log("Sign in attempt using username as identity failed - retrying using email instead...");
        try {
          response = await axios({
            method: 'post',
            url: process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/by-email/',
            headers: { "Content-Type": "application/json" },
            data: JSON.stringify({ "email": identity, "password": password })
          });
          if (response.data.username) {
            username = response.data.username;
            result = 'success';
          } else {
            result = 'fail';
          }
        } catch (error) {
          if (error.code === "ERR_BAD_REQUEST") {
            result = 'fail';
          } else {
            result = 'error'
          }
        }
      }
      console.log('Sign in attempt result: ' + result);

      if (result === 'error') {
        this.setState({
          password: '',
          feedback: 'Something went wrong - Please try again later',
          pending: false,
          submitReady: true,
          identityError: false,
          passwordError: false
        });
        return;

      } else if (result === 'fail') {
        this.setState({
          password: '',
          feedback: `Incorrect ${identity.includes('@') ? "email" : "username"} or password - Please try again`,
          pending: false,
          submitReady: true,
          identityError: true,
          passwordError: true
        });

      } else if (result === 'success') {
        this.props.setAuthData({
          accessToken: response.data.access,
          refreshToken: response.data.refresh,
          username: username ?? identity
        });
      }
    }, 1);

    setTimeout(async () => {
      if (this.state.feedbackFlash === true) {
        this.setState({
          feedbackFlash: false,
        });
      }
    }, 300);
  }

  renderFeedback = () => {
    if (this.state.feedback !== '') {
      return <div className={`feedback ${this.state.pending || (!this.state.feedbackFlash) ? "" : "feedback-ready"}`}>
        {this.state.feedback}
      </div>
    } else {
      return null
    }
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="form">
        {this.renderFeedback()}
        <div className={`field ${this.state.identityError ? 'field-error' : ''}`}>
          <label htmlFor="identity">Username or Email</label>
          <input
            type="text"
            id="identity"
            name="identity"
            autoComplete="username"
            value={this.state.identity}
            onChange={this.handleInputChange} />
        </div>
        <div className={`field ${this.state.passwordError ? 'field-error' : ''}`}>
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            autoComplete="current-password"
            value={this.state.password}
            onChange={this.handleInputChange} />
        </div>
        <div>
          {this.state.submitReady === true
            ? <input className="submit submit-ready" type="submit" value="Sign In" />
            : <div className="submit submit-loading"><img src={require("../images/throbber_light.gif")} alt="loading" /></div>
          }
        </div>
      </form>
    );
  }
}

export default SignInForm;