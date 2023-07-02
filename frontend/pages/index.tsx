import { useState } from "react";
import { useRouter } from "next/router";
import { GetServerSidePropsContext } from "next";
import Link from 'next/link';

import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Card from "@mui/material/Card";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';

import { requestWithoutAuthentication } from "@/functions/request"
import { useAuthContext } from "@/contexts/AuthContext";
import getInitialCookieData from "@/functions/cookies";
import ExternalLink from "@/components/ExternalLink";
import { capitalize } from "lodash";

/**
 * The component for the home page
 */
const HomePage = () => {
  const router = useRouter();
  const { username } = useAuthContext();
  const [ email, setEmail ] = useState("");
  const [ emailFeedback, setEmailFeedback ] = useState("");
  const [ open, setOpen ] = useState(false);

  const handleEmailChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value);
  }

  const handleSnackbarWaitlistClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
    setOpen(false);
  }

  const handleSubmit = async (event: React.ChangeEvent<HTMLFormElement>) => {
    event.preventDefault();

    const response = await requestWithoutAuthentication('POST', 'waitlist_entry/', { email });

    if (response) {
      if (response.status === 201) {
        setEmail("");
        setEmailFeedback("");
        setOpen(true);
      } else {
        if (response.data) {
          if (response.data.email && Array.isArray(response.data.email) && response.data.email.length > 0) {
            setEmailFeedback(response.data.email[0]);
          } else {
            setEmailFeedback("");
          }
        }
      }
    }
  }
  
  return (
    <main aria-label="Home Page" style={{fontSize: "1.05em"}}>
      {/* Font size is slightly larger on the home page */}

      <h2>Welcome to Republic of Rome Online</h2>
      <p><i>Experience the intrigue and power struggles of Ancient Rome, right from your browser</i></p>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={{ xs: 3, md: 5 }} style={{margin: "32px 0"}}>
        <Card style={{ padding: "0 15px" }}>
          <section aria-labelledby="notice">
            <h3 id="notice">Early Development Notice</h3>
            <p>Welcome to Republic of Rome Online! We&apos;re in the early stages of developing this fan-made online adaptation of the classic strategy board game <ExternalLink href="https://boardgamegeek.com/boardgame/1513/republic-rome">The Republic of Rome</ExternalLink>. User registration is currently closed as we work to create an immersive Ancient Rome experience. Stay tuned for updates and the opening of user registration. Thank you for your interest!</p>
          </section>
        </Card>
        <Card style={{ padding: "0 15px" }}>
          <section aria-labelledby="wiki">
            <h3 id="wiki">Wiki</h3>
            <p>The Republic of Rome has a complex set of rules codified in a large and intimidating instruction manual. Learning and checking the rules can be a time consuming and often challenging experience. The solution to this problem is the <ExternalLink href="https://wiki.roronline.com/index.php">Republic of Rome Wiki</ExternalLink>. The vision for the wiki is to create a resource that can be used as a player aid by <i>Republic of Rome Online</i> and the <i>Republic of Rome</i> board game players alike.</p>
          </section>
        </Card>
      </Stack>

      <h3 id="waitlist">Join our waitlist</h3>
        <form onSubmit={handleSubmit}>
          <Stack alignItems="start" spacing={2}>
            <TextField required
                error={emailFeedback != ""}
                id="email"
                label="Email"
                onChange={handleEmailChange}
                style={{width: "300px"}}
                helperText={capitalize(emailFeedback)}
                value={email} />
            <Button variant="contained" type="submit">Join waitlist</Button>
          </Stack>
          <Snackbar
          open={open}
          anchorOrigin={{vertical: "top", horizontal: "center"}}
          autoHideDuration={6000}
          onClose={handleSnackbarWaitlistClose}>
            <Alert onClose={handleSnackbarWaitlistClose}>
              You joined our waitlist successfully. Thank you for your interest!
            </Alert>
          </Snackbar>
        </form>

      {username &&
        <section aria-labelledby="features">
          <h3 id="features">Exclusive Features</h3>
          <p>As a logged-in user, you can now discover and explore existing features and demos.</p>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{ xs: 2 }}>
            <Button variant="contained" LinkComponent={Link} href="/games">Browse Games</Button>
            <Button variant="contained" LinkComponent={Link} href="/demo">UI Components Demo</Button>
          </Stack>
        </section>}
    </main>
  )
}

export default HomePage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { clientAccessToken, clientRefreshToken, clientUsername } = getInitialCookieData(context);
  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUsername: clientUsername
    }
  };
};
