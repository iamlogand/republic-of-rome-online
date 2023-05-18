import { GetServerSidePropsContext } from "next";
import Link from 'next/link';

import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import Card from "@mui/material/Card";

import { useAuthContext } from "@/contexts/AuthContext";
import getInitialCookieData from "@/functions/cookies";
import ExternalLink from "@/components/ExternalLink";

/**
 * The component for the home page
 */
const HomePage = () => {
  const { username } = useAuthContext();
  
  return (
    <main aria-label="Home Page">
      <h2>Welcome to Republic of Rome Online</h2>
      <p><i>Experience the intrigue and power struggles of Ancient Rome, right from your browser</i></p>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={{ xs: 3, md: 5 }} style={{margin: "32px 0"}}>
        <Card variant="outlined" style={{padding: "0 15px", color: "inherit"}}>
          <section aria-labelledby="notice">
            <h3 id="notice">Early Development Notice</h3>
            <p>Welcome to Republic of Rome Online! We&apos;re in the early stages of developing this fan-made online adaptation of the classic strategy board game <ExternalLink href="https://boardgamegeek.com/boardgame/1513/republic-rome">The Republic of Rome</ExternalLink>. User registration is currently closed as we work to create an immersive Ancient Rome experience. Stay tuned for updates and the opening of user registration. Thank you for your interest!</p>
          </section>
        </Card>
        <Card variant="outlined" style={{padding: "0 15px", color: "inherit"}}>
          <section aria-labelledby="wiki">
            <h3 id="wiki">Wiki</h3>
            <p>The Republic of Rome has a complex set of rules codified in a large and intimidating instruction manual. Learning and checking the rules can be a time consuming and often challenging experience. The solution to this problem is the <ExternalLink href="https://wiki.roronline.com/index.php">Republic of Rome Wiki</ExternalLink>. The vision for the wiki is to create a resource that can be used as a player aid by <i>Republic of Rome Online</i> and the <i>Republic of Rome</i> board game players alike.</p>
          </section>
        </Card>
      </Stack>

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
