import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div>
      <h1>Republic of Rome Online</h1>
      <div className="row">
        <h3>Play:</h3>
        <div><Link to="/join-game">Join Game</Link></div>
        <div><Link to="/#">Create Game</Link></div>
      </div>
    </div>
  )
}
