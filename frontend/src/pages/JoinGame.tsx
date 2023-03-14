import { useEffect, useState } from 'react';
import { Link } from "react-router-dom";
import request from "../helpers/requestHelper"
import TopBar from "../components/TopBar"
import Game from "../objects/Game"
import formatDate from '../helpers/dateHelper';

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
  const [gamesList, setGamesList] = useState<Game[]>()

  const fetchGames = async () => {
    const response = await request('get', 'games/', props.accessToken, props.refreshToken, props.setAuthData);
    if (response && response.data) {
      let games: Game[] = [];
      for (let i = 0; i < response.data.length; i++) {
        const object = response.data[i];
        const game = new Game(
          object["name"],
          object["owner"] && object["owner"]["username"] ? object["owner"]["username"] : null,
          object["description"] ? object["description"] : null,
          object["creation_date"] ? new Date(object["creation_date"]) : null,
          object["start_date"] ? new Date(object["start_date"]) : null
        );
        games.push(game);
      }
      setGamesList(games);
    }
  }

  useEffect(() => {
    fetchGames();
  }, [props.accessToken, props.refreshToken, props.setAuthData]);

  const refresh = () => {
    fetchGames();
  }

  return (
    <div id="page_container">
      <TopBar username={props.username} />
      <div id="standard_page">
        <div id="page_content">
          <h1>Republic of Rome Online</h1>
          <p><Link to="/">Back to Main Menu</Link></p>
          <h3>Existing Games:</h3>
          <p><a href="#" onClick={refresh}>Refresh</a></p>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Owner</th>
                <th>Description</th>
                <th>Creation Date</th>
                <th>Start Date</th>
              </tr>
            </thead>
            {gamesList && gamesList.length > 0 && gamesList.map((game, index) =>
              <tbody>
                <tr key={index}>
                  <td>{game.name}</td>
                  <td>{game.owner}</td>
                  <td>{game.description}</td>
                  <td>
                    {game.creationDate && game.creationDate instanceof Date &&
                      formatDate(game.creationDate)
                    }
                  </td>
                  <td>
                    {game.startDate && game.startDate instanceof Date &&
                      formatDate(game.startDate)
                    }
                  </td>
                </tr>
              </tbody>
            )}
          </table>
        </div>
      </div>
    </div>
  );
}

export default JoinGame;
