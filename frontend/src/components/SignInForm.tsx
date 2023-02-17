import { useState } from 'react';
import axios from "axios";

interface SignInFormProps {
  setAuthData: Function
}

/**
 * The component for the sign in form for existing users
 */
const SignInForm = (props: SignInFormProps) => {
  const [identity, setIdentity] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');
  const [identityError, setIdentityError] = useState<boolean>(false);
  const [passwordError, setPasswordError] = useState<boolean>(false);
  const [pending, setPending] = useState<boolean>(false);

  const handleInputChange = (event: any) => {
    // Update the `identity` and `password` states whenever the field values are altered
    if (event.target.name === 'identity') {
      setIdentity(event.target.value);
    } else if (event.target.name === "password") {
      setPassword(event.target.value);
    }
  }

  // Process a click of the submission button
  const handleSubmit = async (event: any) => {
    event.preventDefault();  // Prevent default form submission behavior

    if (identity === '' && password === '') {
      // The identity and password fields are empty
      setFeedback('Please enter your sign in credentials');
      setIdentityError(true);
      setPasswordError(true);
      return;

    } else if (identity === '') {
      // The identity field is empty
      setFeedback('Please enter your username or email');
      setIdentityError(true);
      setPasswordError(false);
      return;

    } else if (password === '') {
      // The password field is empty
      setFeedback('Please enter your password');
      setIdentityError(false);
      setPasswordError(true);
      return;
    }

    // With the basic checks passing, temporarily disable the submit button
    // and render a throbber in it's place
    setPending(true);

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
      } catch (error: any) {
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
      setPassword('');
      setFeedback('Something went wrong - please try again later');
      setPending(false);
      setIdentityError(false);
      setPasswordError(false);
      return;

    } else if (result === 'fail') {
      setPassword('');
      setFeedback(`Incorrect ${identity.includes('@') ? "email" : "username"} or password - please try again`);
      setPending(false);
      setIdentityError(true);
      setPasswordError(true);

    } else if (result === 'success' && response) {
      // If the sign in request succeeded, set the username and JWT tokens.
      // Setting these states will cause the router to navigate away from the sign in page
      props.setAuthData({
        accessToken: response.data.access,
        refreshToken: response.data.refresh,
        username: username ?? identity
      });
    }
  }

  // Render the feedback message
  const renderFeedback = () => {
    if (feedback !== '') {
      // Feedback is shown if something went wrong with submission
      return (
        <div className='auth_feedback'>
          {feedback}
        </div>
      )
    } else {
      // No feedback
      return null
    }
  }

  return (
    <form onSubmit={handleSubmit} className="auth_form">

      {renderFeedback()} {/* The feedback message */}

      {/* The identity field */}
      <div className={`auth_field ${identityError ? 'auth_field_error' : ''}`}>
        <label htmlFor="identity">Username or Email</label>
        <input
          type="text"
          id="identity"
          name="identity"
          autoComplete="username"
          value={identity}
          onChange={handleInputChange} />
      </div>

      {/* The password field */}
      <div className={`auth_field ${passwordError ? 'auth_field_error' : ''}`}>
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          autoComplete="current-password"
          value={password}
          onChange={handleInputChange} />
      </div>

      {/* The submit button */}
      <div>
        {pending === false
          ? <input className="auth_submit auth_submit_ready" type="submit" value="Sign In" />
          : <div className="auth_submit auth_submit_loading"><img src={require("../images/throbber_light.gif")} alt="loading" /></div>
        }
      </div>
    </form>
  );
}

export default SignInForm;
