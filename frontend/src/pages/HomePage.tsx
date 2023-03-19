import { Link } from "react-router-dom";

interface HomeProps {
  username: string
}

/**
 * The component for the home page
 */
const Home = (props: HomeProps) => {
  return (
    <main id="standard_page" aria-label="Home Page">
      <section aria-labelledby="page-title">
        <h2 id="page-title">Welcome to Republic of Rome Online</h2>
        <p><i>Experience the intrigue and power struggles of Ancient Rome, right from your browser</i></p>
      </section>
      
      <section aria-labelledby="notice">
        <h3 id="notice">Early Development Notice</h3>
        <p>Welcome to Republic of Rome Online! We're in the early stages of developing this online adaptation of the classic strategy board game. User registration is currently closed as we work to create an immersive Ancient Rome experience. Stay tuned for updates and the opening of user registration. Thank you for your interest!</p>
      </section>

      {props.username &&
      <section aria-labelledby="features">
        <h3 id="features">Exclusive Features</h3>
        <p>As a logged-in user, you can now discover and explore existing features and demos.</p>
        <ul className='row'>
          <li><Link to="/join-game" className="button" style={{width: "150px"}}>Browse Games</Link></li>
          <li><Link to="/game" className="button" style={{width: "210px"}}>UI Components Demo</Link></li>
        </ul>
      </section>}
    </main>
  )
}

export default Home;
