import { GetServerSidePropsContext } from "next";
import { useAuth } from "../contexts/AuthContext";
import Button from '@/components/Button';
import getInitialCookieData from "@/helpers/cookiesHelper";

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
        <p>Welcome to Republic of Rome Online! We&apos;re in the early stages of developing this fan-made online adaptation of the classic strategy board game <a href="https://boardgamegeek.com/boardgame/1513/republic-rome" className="link">The Republic of Rome</a>. User registration is currently closed as we work to create an immersive Ancient Rome experience. Stay tuned for updates and the opening of user registration. Thank you for your interest!</p>
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
