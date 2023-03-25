import { useState } from 'react';
import axios from "axios";
import { useAuth } from '../AuthContext';

interface SignInDialogProps {
  setDialog: Function
}

/**
 * The component for the sign in form for existing users
 */
const SignInDialog = (props: SignInDialogProps) => {
  const { setAccessToken, setRefreshToken, setUsername } = useAuth();
  const [identity, setIdentity] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');
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

    // Temporarily disable the submit button and render a throbber in it's place
    setPending(true);

    let response;
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
      return;

    } else if (result === 'fail') {
      setPassword('');
      setFeedback(`Incorrect ${identity.includes('@') ? "email" : "username"} or password - please try again`);
      setPending(false);

    } else if (result === 'success' && response) {
      // If the sign in request succeeded, set the username and JWT tokens
      setAccessToken(response.data.access);
      setRefreshToken(response.data.refresh);
      setUsername(identity);
      props.setDialog('')
    }
  }

  const handleCancel = () => {
    props.setDialog('')
  }

  return (
    <div className='dialog-container'>
      <dialog open>
        <h2>Sign in</h2>
        <form onSubmit={handleSubmit} style={{padding: "20px"}}>

          {/* Validation feedback */}
          { feedback && (
          <div className={`feedback ${feedback !== '' ? 'active' : ''}`}>
            <strong>{feedback}</strong>
          </div>
          )}

          {/* The identity field */}
          <label htmlFor="identity" className={feedback && 'error'}>Username or Email</label>
          <input required
            type="text"
            id="identity"
            name="identity"
            autoComplete="username"
            value={identity}
            onChange={handleInputChange}
            className={`field ${feedback && 'error'}`} />

          {/* The password field */}
          <label htmlFor="password" className={feedback && 'error'}>Password</label>
          <input required
            type="password"
            id="password"
            name="password"
            autoComplete="current-password"
            value={password}
            onChange={handleInputChange}
            className={`field ${feedback && 'error'}`} />

          {/* The buttons */}
            <div className='row' style={{marginTop: "5px", justifyContent: "space-evenly", width: "100%"}}>
              <button type="button" onClick={handleCancel} className="button" style={{width: "90px"}}>Cancel</button>
              {pending ?
              <div className="button loading" style={{width: "90px"}}>
                <img src={require("../images/throbber.gif")} alt="loading" />
              </div> :
              <input type="submit" value="Sign In" className="button" style={{width: "90px"}} />}
            </div>
        </form>
      </dialog>
    </div>
  );
}

export default SignInDialog;
