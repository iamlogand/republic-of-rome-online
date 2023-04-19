import { GetServerSidePropsContext } from "next";
import { useAuth } from "../contexts/AuthContext";
import Button from '@/components/Button';
import getInitialCookieData from "@/helpers/cookies";

/**
 * The component for the home page
 */
const HomePage = () => {
  const { username } = useAuth();

  return (
    <main aria-label="Home Page">
      <section aria-labelledby="page-title">
        <h2 id="page-title">Welcome to Republic of Rome Online</h2>
        <p><i>Experience the intrigue and power struggles of Ancient Rome, right from your browser</i></p>
      </section>

      <section aria-labelledby="notice">
        <h3 id="notice">Early Development Notice</h3>
        <p>Welcome to Republic of Rome Online! We&apos;re in the early stages of developing this fan-made online adaptation of the classic strategy board game <a href="https://boardgamegeek.com/boardgame/1513/republic-rome" className="link" target="_blank">The Republic of Rome</a>. User registration is currently closed as we work to create an immersive Ancient Rome experience. Stay tuned for updates and the opening of user registration. Thank you for your interest!</p>
      </section>

      <section aria-labelledby="wiki">
        <h3 id="wiki">Wiki</h3>
        <p>The Republic of Rome has a complex set of rules codified in a large and intimidating instruction manual. Learning and checking the rules can be a time consuming and often challenging experience. The solution to this problem is the <a href="https://wiki.roronline.com/index.php" className="link" target="_blank">Republic of Rome Wiki</a>. The vision for the wiki is to create a resource that can be used as a player aid by <i>Republic of Rome Online</i> and the <i>Republic of Rome</i> board game players alike.</p>
      </section>

      {username &&
        <section aria-labelledby="features">
          <h3 id="features">Exclusive Features</h3>
          <p>As a logged-in user, you can now discover and explore existing features and demos.</p>
          <ul className='row'>
            <li><Button href="/games">Browse Games</Button></li>
            <li><Button href="/games/new">Create Game</Button></li>
            <li><Button href="/demo">UI Components Demo</Button></li>
          </ul>
        </section>}
    </main>
  )
}

export default HomePage;

export const getServerSideProps = async (context: GetServerSidePropsContext) => {
  const { accessToken, refreshToken, username } = getInitialCookieData(context);
  return {
    props: {
      ssrAccessToken: accessToken,
      ssrRefreshToken: refreshToken,
      ssrUsername: username
    }
  };
};
