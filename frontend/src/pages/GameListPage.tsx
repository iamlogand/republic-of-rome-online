import { useEffect, useState, useCallback } from 'react';
import { Link } from "react-router-dom";
import request from "../helpers/requestHelper"
import Game from "../objects/Game"
import formatDate from '../helpers/dateHelper';

interface GameListPageProps {
  accessToken: string,
  refreshToken: string,
  setAccessToken: Function,
  setRefreshToken: Function,
  setUsername: Function
}

/**
 * The component for the join game page
 */
const GameListPage = (props: GameListPageProps) => {
  const [gameList, setGameList] = useState<Game[]>([]);
  const [elapsedMinutes, setElapsedMinutes] = useState(0);
  const [refreshPending, setRefreshPending] = useState<boolean>(false);

  // On game list update, start and reset an interval for the elapsed time message 
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedMinutes((prevMinutes) => prevMinutes + 1);
    }, 60000); // Update every 60000ms (1 minute)

    return () => {
      clearInterval(interval);
    };
  }, [gameList])

  // Refresh the game list
  const refreshGame = useCallback(async () => {
    const response = await request('GET', 'games/', props.accessToken, props.refreshToken, props.setAccessToken, props.setRefreshToken, props.setUsername);
    if (response && response.data) {
      let games: Game[] = [];
      for (let i = 0; i < response.data.length; i++) {
        const object = response.data[i];
        const game = new Game(
          object["name"],
          object["owner"] ?? null,
          object["description"] ?? null,
          object["creation_date"] ?? null,
          object["start_date"] ?? null
        );
        games.push(game);
      }
  
      games.sort((a, b) => {
        const aDate = new Date(a.creationDate);
        const bDate = new Date(b.creationDate);
        return bDate.getTime() - aDate.getTime();
      });
  
      setGameList(games);
    }
  }, [props.accessToken, props.refreshToken, props.setAccessToken, props.setRefreshToken, props.setUsername]);

  // On page load, refresh the game list because it's initially empty
  useEffect(() => {
    const fetchGames = async () => {
      await refreshGame();
    };
  
    fetchGames();
  }, [refreshGame]);

  // Process a click of the submission button
  const handleRefresh = async () => {
    setGameList([]);
    setRefreshPending(true);

    setTimeout(async () => {
      await refreshGame();
      setElapsedMinutes(0);
      setRefreshPending(false);
    }, 500);
    
  }

  const renderElapsedTimeMessage = () => {
    if (elapsedMinutes === 0) {
      return "just now";
    } else if (elapsedMinutes === 1) {
      return "1 minute ago";
    } else if (elapsedMinutes > 59) {
      return "over an hour ago";
    } else {
      return `${elapsedMinutes} minutes ago`;
    }
  }

  return (
    <main id="standard_page">
      <section className='row' style={{justifyContent: "space-between"}}>
        <div className='row'>
          <Link to=".." className="button" style={{width: "90px"}}>◀&nbsp; Back</Link>
          <h2>Browse Games</h2>
        </div>
        <div className='row'>
          <p className='no-margin'>
            Last updated {renderElapsedTimeMessage()}
          </p>
          {refreshPending ?
            <div className='button loading' style={{width: "95px"}}>
              <img src={require("../images/throbber.gif")} alt="loading" />
            </div> :
            <button onClick={handleRefresh} className='button' style={{width: "95px"}}>Refresh</button>}
        </div>
      </section>
      
      <section>
        <div className='table-container'>
          <table style={{tableLayout: "fixed", minWidth: "700px"}}>
            <thead>
              <tr>
                <th>Name</th>
                <th>Owner</th>
                <th>Description</th>
                <th>Creation Date</th>
                <th>Start Date</th>
              </tr>
            </thead>

            {gameList && gameList.length > 0 && gameList.map((game, index) =>
              <tbody key={index}>
                <tr>
                  <td className='no-wrap-ellipsis'>{game.name}</td>
                  <td className='no-wrap-ellipsis'>{game.owner}</td>
                  <td className='no-wrap-ellipsis'>{game.description ? game.description : ''}</td>
                  <td>{game.creationDate && game.creationDate instanceof Date && formatDate(game.creationDate)}</td>
                  <td>{game.startDate && game.startDate instanceof Date && formatDate(game.startDate)}</td>
                </tr>
              </tbody>
            )}
          </table>
        </div>
        {gameList && gameList.length > 0 && <p>Showing all {gameList?.length} games</p>}
      </section>
    </main>
  );
}

export default GameListPage;
