import { Ref, useCallback, useEffect, useRef, useState } from 'react';
import axios from "axios";
import { useRouter } from 'next/router';

import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import { useTheme } from '@mui/material/styles';

import { useAuthContext } from '@/contexts/AuthContext';
import useFocusTrap from '@/hooks/useFocusTrap';
import ModalTitle from '@/components/modals/ModalTitle';

interface SignInModalProps {
  setModal: Function;
  sessionExpired?: boolean;
}

/**
 * The component for the sign in form for existing users
 */
const SignInModal = (props: SignInModalProps) => {
  const { setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const [identity, setIdentity] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [feedback, setFeedback] = useState<string>('');
  const router = useRouter();
  const modalRef: Ref<HTMLDialogElement> = useRef(null);
  const theme = useTheme();

  useFocusTrap(modalRef);

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

    let response;
    let result;

    // Request a new pair of JWT tokens using the identity as a username
    try {
      response = await axios({
        method: 'post',
        url: process.env.NEXT_PUBLIC_API_URL + 'tokens/',
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
          url: process.env.NEXT_PUBLIC_API_URL + 'tokens/email/',
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
      return;

    } else if (result === 'fail') {
      setPassword('');
      setFeedback(`Incorrect ${identity.includes('@') ? "email" : "username"} or password - please try again`);

    } else if (result === 'success' && response) {
      // If the sign in request succeeded, set the username and JWT tokens
      setAccessToken(response.data.access);
      setRefreshToken(response.data.refresh);
      setUsername(response.data.username ?? identity);
      props.setModal('')
    }
  }

  const handleCancel = useCallback(async () => {
    if (props.sessionExpired) {
      await router.push('/');
      props.setModal('')
    } else {
      props.setModal('')
    }
  }, [props, router]);

  // Close modal using ESC key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        handleCancel();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleCancel]);

  return (
    <dialog open aria-modal="true" ref={modalRef} >
      <ModalTitle title="Sign in"
        closeAction={handleCancel}
        ariaLabel={props.sessionExpired ? "Return home" : "Cancel"}
      />

      <form onSubmit={handleSubmit} style={{ padding: "20px" }}>
        <Stack alignItems={"start"} spacing={2}>
          {/* Validation feedback */}
          {feedback && (
            <p style={{ maxWidth: "300px", marginTop: "0", color: theme.palette.error.main }}>{feedback}</p>
          )}

          {/* The identity field */}
          <TextField required
            type="text"
            name="identity"
            label="Username or Email"
            autoComplete="username"
            value={identity}
            onChange={handleInputChange}
            style={{width: "300px"}}
            error={feedback != ""} />

          {/* The password field */}
          <TextField required
            type="password"
            name="password"
            label="Password"
            autoComplete="current-password"
            value={password}
            onChange={handleInputChange}
            style={{width: "300px"}}
            error={feedback != ""} />

          {/* The buttons */}
          <Stack direction="row" justifyContent="space-around" spacing={2} style={{width: "100%"}}>
            <Button variant="contained" onClick={handleCancel}>{props.sessionExpired ? "Return home" : "Cancel"}</Button>
            <Button type="submit" variant="contained">Sign in</Button>
          </Stack>
        </Stack>
      </form>
    </dialog>
  );
}

export default SignInModal;
