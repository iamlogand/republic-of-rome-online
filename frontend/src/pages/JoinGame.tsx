import { useEffect, useState } from 'react';
import { Link } from "react-router-dom";
import request from "../helpers/requestHelper"
import TopBar from "../components/TopBar"
import Game from "../objects/Game"

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

  useEffect(() => {
    const fetchData = async () => {
      const response = await request('get', 'games/', props.accessToken, props.refreshToken, props.setAuthData);
      if (response && response.data) {
        let games: Game[] = [];
        for (let i = 0; i < response.data.length; i++) {
          const object = response.data[i];
          const game = new Game(
            object["name"],
            object["owner"]["username"],
            object["description"],
            object["creation_date"] ? new Date(object["creation_date"]) : null,
            object["start_date"] ? new Date(object["start_date"]) : null
          );
          games.push(game);
        }
        setGamesList(games);
      }
    }
    fetchData();
  }, [props.accessToken, props.refreshToken, props.setAuthData]);

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
            <table>
              <tr>
                <th>Name</th>
                <th>Owner</th>
                <th>Description</th>
                <th>Creation Date</th>
                <th>Start Date</th>
              </tr>
              {gamesList && gamesList.length > 0 && gamesList.map((game, index) =>
                <tr key={index}>
                  <td>{game.name}</td>
                  <td>{game.owner}</td>
                  <td>{game.description}</td>
                  <td>
                    {game.creationDate && game.creationDate instanceof Date &&
                      game.creationDate.toDateString() + " " + game.creationDate.toTimeString()
                    }
                  </td>
                  <td>
                    {game.startDate && game.startDate instanceof Date &&
                      game.startDate.toDateString() + " " + game.startDate.toTimeString()
                    }
                  </td>
                </tr>
              )}
            </table>
            
          </div>
        </div>
      </div>
    </div>
  );
}

export default JoinGame;
