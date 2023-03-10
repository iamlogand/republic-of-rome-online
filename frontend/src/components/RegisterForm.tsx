import { useState } from 'react';
import axios from "axios";

interface RegisterFormProps {
  setAuthData: Function
}

/**
 * The component for the registration form for new users
 * Currently unfinished
 */
const RegisterForm = (props: RegisterFormProps) => {
  const [username, setUsername] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password1, setPassword1] = useState<string>('');
  const [password2, setPassword2] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');
  const [pending, setPending] = useState<boolean>(false);

  const handleInputChange = (event: any) => {
    if (event.target.name === 'username') {
      setUsername(event.target.value);
    } else if (event.target.name === "email") {
      setEmail(event.target.value);
    } else if (event.target.name === "password1") {
      setPassword1(event.target.value);
    } else if (event.target.name === "password2") {
      setPassword2(event.target.value);
    }
  }

  const handleSubmit = (event: any) => {
    event.preventDefault();  // Prevent default form submission behavior

    setPending(true);

    setTimeout(async () => {
      if (username === '' || password1 === '') {
        setFeedback('Please provide a username and password.');
        setPending(false);
      } else if (password2 === '') {
        setFeedback('Please confirm your new password.');
        setPending(false);
      } else if (password1 !== password2) {
        setFeedback("Those passwords don't match. Please try again.");
        setPending(false);
      } else {

        const data = JSON.stringify({
          "username": username,
          "password": password1
        });

        try {
          await axios({
            method: 'post',
            url: process.env.REACT_APP_BACKEND_ORIGIN + '/rorapp/api/token/',
            headers: { "Content-Type": "application/json" },
            data: data
          });
        } catch (error: any) {

          if (error && error.code === "ERR_BAD_REQUEST") {
            setPassword1('');
            setPassword2('');
            setFeedback('Your username and password do not match. Please try again.');
            setPending(false);
          } else {
            setPassword1('');
            setPassword2('');
            setFeedback('Something went wrong. Please try again later.');
            setPending(false);
          }
          return;
        }
      }
    }, 1);
  }

  return (
    <form onSubmit={handleSubmit} className="auth_form">
      
      { feedback && (
      <div className={`feedback ${feedback !== '' ? 'active' : ''}`}>
        <strong>{feedback}</strong>
      </div>
      )}

      <label htmlFor="username" className={feedback && 'error'}>Username</label>
      <input
        type="text"
        id="username"
        name="username"
        autoComplete="username"
        value={username}
        onChange={handleInputChange}
        className="field" />
      <label htmlFor="email" className={feedback && 'error'}>Email</label>
      <input
        type="text"
        id="email"
        name="email"
        autoComplete="email"
        value={email}
        onChange={handleInputChange}
        className="field" />
      <label htmlFor="password1" className={feedback && 'error'}>Password</label>
      <input
        type="password"
        id="password1"
        name="password1"
        autoComplete="new-password"
        value={password1}
        onChange={handleInputChange}
        className="field" />
      <label htmlFor="password2" className={feedback && 'error'}>Confirm Password</label>
      <input
        type="password"
        id="password2"
        name="password2"
        autoComplete="new-password"
        value={password2}
        onChange={handleInputChange}
        className="field" />

      {/* The submit button */}
      {pending === false
        ? <input className="submit ready" type="submit" value="Sign In" />
        : (
            <div className="submit loading">
              <img src={require("../images/throbber.gif")} alt="loading" />
            </div>
          )
      }
    </form>
  );
}

export default RegisterForm;
