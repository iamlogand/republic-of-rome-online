import { Component } from 'react';
import axios from "axios";

/**
 * The component for the sign in form for existing users
 */
class SignInForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      identity: '',  // The value in the identity field (can be username or email address)
      password: '',  // The value in the password field
      feedback: '',  // The current feedback message
      identityError: false,  // `true` when the identity field has errored
      passwordError: false,  // `true` when the password field has errored
      pending: false  // `true` when submit button is disabled and waiting for submission resolution
    };

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleInputChange(event) {
    // Update the `identity` and `password` states whenever the field values are altered
    if (event.target.name === 'identity') {
      this.setState({ identity: event.target.value });
    } else if (event.target.name === "password") {
      this.setState({ password: event.target.value });
    }
  }

  // Process a click of the submission button
  async handleSubmit(event) {
    event.preventDefault();  // Prevent default form submission behavior

    // Read these only once, in case they change part way through execution
    const identity = this.state.identity;
    const password = this.state.password;

    if (identity === '' && password === '') {
      // The identity and password fields are empty
      this.setState({
        feedback: 'Please enter your sign in credentials',
        identityError: true,
        passwordError: true
      });
      return;

    } else if (identity === '') {
      // The identity field is empty
      this.setState({
        feedback: 'Please enter your username or email',
        identityError: true,
        passwordError: false
      });
      return;
      
    } else if (password === '') {
      // The password field is empty
      this.setState({
        feedback: 'Please enter your password',
        identityError: false,
        passwordError: true
      });
      return;
    }

    // With the basic checks passing, temporarily disable the submit button
    // and render a throbber in it's place
    this.setState({
      pending: true
    });

    let response;
    let username;
    let result;

    // Request a new pair of JWT tokens using the identity as a username
    try {
      response = await axios({
        method: 'post',
        url: process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/',
        headers: { "Content-Type": "application/json" },
        data: JSON.stringify({ "username": identity, "password": password })
      });
      result = 'success';
    } catch (error) {

      // If that fails, request a new pair of JWT tokens using the identity as an email address
      console.log("Sign in attempt using username as identity failed - retrying using email instead...");
      try {
        response = await axios({
          method: 'post',
          url: process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/email/',
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

    // If the sign in request errored or failed, clear password and set a feedback message 
    if (result === 'error') {
      this.setState({
        password: '',
        feedback: 'Something went wrong - please try again later',
        pending: false,
        identityError: false,
        passwordError: false
      });
      return;
    } else if (result === 'fail') {
      this.setState({
        password: '',
        feedback: `Incorrect ${identity.includes('@') ? "email" : "username"} or password - please try again`,
        pending: false,
        identityError: true,
        passwordError: true
      });

    } else if (result === 'success') {
      // If the sign in request succeeded, set the username and JWT tokens.
      // Setting these states will cause the router to navigate away from the sign in page
      this.props.setAuthData({
        accessToken: response.data.access,
        refreshToken: response.data.refresh,
        username: username ?? identity
      });
    }
  }

  // Render the feedback message
  renderFeedback = () => {
    if (this.state.feedback !== '') {
      // Feedback is shown if something went wrong with submission
      return (
        <div className='auth_feedback'>
          {this.state.feedback}
        </div>
      )
    } else {
      // No feedback
      return null
    }
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit} className="auth_form">

        {this.renderFeedback()} {/* The feedback message */}

        {/* The identity field */}
        <div className={`auth_field ${this.state.identityError ? 'auth_field_error' : ''}`}>
          <label htmlFor="identity">Username or Email</label>
          <input
            type="text"
            id="identity"
            name="identity"
            autoComplete="username"
            value={this.state.identity}
            onChange={this.handleInputChange} />
        </div>

        {/* The password field */}
        <div className={`auth_field ${this.state.passwordError ? 'auth_field_error' : ''}`}>
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            autoComplete="current-password"
            value={this.state.password}
            onChange={this.handleInputChange} />
        </div>

        {/* The submit button */}
        {this.state.pending === false
          ? <input className="auth_submit auth_submit_ready" type="submit" value="Sign In" />
          : <div className="auth_submit auth_submit_loading"><img src={require("../images/throbber.gif")} alt="loading" /></div>
        }
      </form>
    );
  }
}

export default SignInForm;
