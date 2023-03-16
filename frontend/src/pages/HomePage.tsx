import { Link } from "react-router-dom";
import TopBar from "../components/TopBar"

interface HomeProps {
  username: string
}

/**
 * The component for the home page
 */
const Home = (props: HomeProps) => {
  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div id="standard_page">
        <header>
          <h1>Welcome to Republic of Rome Online</h1>
          <p><i>Experience the intrigue and power struggles of Ancient Rome, right from your browser</i></p>
        </header>
        
        <section>
          <h2>Early Development Notice</h2>
          <p>Welcome to Republic of Rome Online! We're in the early stages of developing this online adaptation of the classic strategy board game. User registration is currently closed as we work to create an immersive Ancient Rome experience. Stay tuned for updates and the opening of user registration. Thank you for your interest!</p>
        </section>

        {props.username &&
        <section>
          <h2>Exclusive Features</h2>
          <p>As a logged-in user, you can now discover and explore existing features and demos.</p>
          <div className='row' style={{margin: "25px 0"}}>
            <Link to="/join-game" className="button" style={{width: "150px"}}>Browse Games</Link>
            <Link to="/game" className="button" style={{width: "210px"}}>UI Components Demo</Link>
          </div>
        </section>}
      </div>
    </div>
  )
}

export default Home;
