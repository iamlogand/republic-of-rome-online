import { useEffect, useState, useCallback } from 'react';
import { GetServerSidePropsContext } from 'next';
import { useAuth } from '@/contexts/AuthContext';
import request from "@/helpers/requestHelper"
import formatDate from '@/helpers/dateHelper';
import Game from "@/classes/Game"
import Button from '@/components/Button';
import { AxiosResponse } from 'axios';
import getInitialCookieData from '@/helpers/cookiesHelper';

/**
 * The component for the game list page
 */
const GamesPage = ({ initialGameList }: { initialGameList: string[] }) => {
  const { accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername } = useAuth();
  const [gameList, setGameList] = useState<Game[]>(
    initialGameList.map((gameString) => {
      const gameObj = JSON.parse(gameString);
      return new Game(
        gameObj.name,
        gameObj.owner,
        gameObj.description,
        new Date(gameObj.creationDate),
        gameObj.startDate ? new Date(gameObj.startDate) : null
      );
    })
  );
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [refreshPending, setRefreshPending] = useState<boolean>(false);

  // On game list update, start and reset an interval for the elapsed time message 
  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedSeconds((prevMinutes) => prevMinutes + 1);
    }, 1000); // Update every 1000ms (1 second)

    return () => {
      clearInterval(interval);
    };
  }, [gameList])

  // Refresh the game list
  const refreshGames = useCallback(async () => {
    const response = await request('GET', 'games/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
    const games = getGames(response);
    setGameList(games);
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername]);

  // Process a click of the submission button
  const handleRefresh = async () => {
    setRefreshPending(true);
    await refreshGames();
    setElapsedSeconds(0);
    setRefreshPending(false);
  }

  return (
    <main id="standard_page">
      <section className='row' style={{justifyContent: "space-between"}}>
        <div className='row'>
          <Button href="..">◀ Back</Button>
          <h2>Browse Games</h2>
        </div>
        <div className='row'>
          <p className='no-margin'>
            Last updated {elapsedSeconds !== 0 ? elapsedSeconds + "s ago": "now"}
          </p>
          <Button onClick={handleRefresh} pending={refreshPending} width={90}>Refresh</Button>
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

const getGames = (response: AxiosResponse) => {
  let games: Game[] = [];

  if (response && response.data) {
    for (let i = 0; i < response.data.length; i++) {
      const object = response.data[i];
      const game = new Game(
        object["name"],
        object["owner"],
        object["description"] ?? null,
        new Date(object["creation_date"]),
        object["start_date"] ? new Date(object["start_date"]) : null
      );
      games.push(game);
    }

    games.sort((a, b) => {
      const aDate = new Date(a.creationDate);
      const bDate = new Date(b.creationDate);
      return bDate.getTime() - aDate.getTime();
    });
  }
  return games;
};


export default GamesPage;

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { accessToken, refreshToken, username } = getInitialCookieData(context);
  const response = await request('GET', 'games/', accessToken, refreshToken);
  const games = getGames(response).map((game) => JSON.stringify(game));

  return {
    props: {
      ssrAccessToken: accessToken,
      ssrRefreshToken: refreshToken,
      ssrUsername: username,
      initialGameList: games,
    },
  };
}
