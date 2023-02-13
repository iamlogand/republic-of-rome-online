import { useEffect, useState } from 'react';
import { Link } from "react-router-dom";
import request from "../helpers/RequestHelper"
import TopBar from "../components/TopBar"

interface JoinGameProps {
  accessToken: string,
  refreshToken: string,
  username: string
  setAuthData: Function
}

/**
 * The component for the join game page
 */
const JoinGame = (props: JoinGameProps) => {
  const [gamesList, setGamesList] = useState<any[]>()

  useEffect(() => {
    const fetchData = async () => {
      const response = await request('get', 'games/', props.accessToken, props.refreshToken, props.setAuthData);
      if (response) {
        setGamesList(response.data);
      }
    }
    fetchData();
  }, [props.accessToken, props.refreshToken, props.setAuthData]);

  const renderGames = () => {
    if (gamesList && gamesList.length > 0) {
      return gamesList.map(game => (<div key={game.name}>{game.name}</div>));
    } else {
      return 'None';
    }
  }

  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div id="standard_page">
        <div id="page_content">
          <h1>Republic of Rome Online</h1>
          <div>
            <Link to="/">Back to Main Menu</Link>
          </div>
          <div>
            <h3>Existing Games:</h3>
            {renderGames()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default JoinGame;
