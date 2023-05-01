import { useEffect, useState, useCallback, useRef } from 'react';
import { GetServerSidePropsContext } from 'next';
import { useAuthContext } from '@/contexts/AuthContext';
import request, { ResponseType } from "@/functions/request"
import formatDate from '@/functions/date';
import Game from "@/classes/Game"
import Button from '@/components/Button';
import getInitialCookieData from '@/functions/cookies';
import Head from 'next/head';
import { useModalContext } from '@/contexts/ModalContext';
import PageError from '@/components/PageError';
import ClickableTableRow from '@/components/LinkedTableRow';
import Breadcrumb from '@/components/Breadcrumb';
import styles from './index.module.css'
import ElapsedTime from '@/components/ElapsedTime';


interface GamesPageProps {
  initialGameList: string[];
}

/**
 * The component for the game list page
 */
const GamesPage = (props: GamesPageProps) => {
  const { username, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const { setModal } = useModalContext();
  const [refreshPending, setRefreshPending] = useState<boolean>(false);
  const [gameList, setGameList] = useState<Game[]>(props.initialGameList.map((gameString) => new Game(JSON.parse(gameString))));
  const [timeResetKey, setTimeResetKey] = useState(gameList.length == 0 ? 0 : 1);

  // Refresh the game list
  const refreshGames = useCallback(async () => {
    const response = await request('GET', 'games/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
    const games = getGames(response);
    setGameList(games);
    setTimeResetKey(e => e + 1);
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername, setTimeResetKey]);

  useEffect(() => {
    if (username != '' && gameList.length == 0) {
      // If game list is empty on page load, perhaps the SSR fetch failed, so try a CSR fetch to ensure sign out if user tokens have expired
      refreshGames();
    }
  
    if (username == '') {
      setModal("sign-in-required");
    }
  }, [username, gameList, refreshGames, setModal]);
  

  // Process a click of the submission button
  const handleRefresh = async () => {
    setRefreshPending(true);
    await refreshGames();
    setRefreshPending(false);
  }

  // Render page error if user is not signed in
  if (username == '') {
    return <PageError statusCode={401} />;
  }

  return (
    <>
      <Head>
        <title>Browse Games - Republic of Rome Online</title>
      </Head>
      <main>
        <Breadcrumb />

        <section className={styles.topRow} style={{justifyContent: "space-between"}}>
          <h2 className={styles.title}>Browse Games</h2>
          <div className={styles.statusArea}>
            {timeResetKey != 0 &&
              <p>
                Last updated <ElapsedTime resetKey={timeResetKey} />
              </p>
            }

            <div className={styles.buttons}>
              <Button onClick={handleRefresh} buttonType={refreshPending ? "pending" : "standard"} width={90}>Refresh</Button>
              <Button href="/games/new">Create Game</Button>
            </div>
          </div>
        </section>
        
        <section>
          <div className='table-container'>
            <table style={{tableLayout: "fixed", minWidth: "700px"}}>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Owner</th>
                  <th>Creation Date</th>
                  <th>Start Date</th>
                </tr>
              </thead>

              {gameList && gameList.length > 0 && gameList.map((game, index) =>
                <tbody key={index}>
                  <ClickableTableRow href={'/games/' + game.id}>
                    <td className='no-wrap-ellipsis'>{game.name}</td>
                    <td className='no-wrap-ellipsis'>{game.owner == username ? <b>You</b> : game.owner}</td>
                    <td>{game.creation_date && game.creation_date instanceof Date && formatDate(game.creation_date)}</td>
                    <td>{game.start_date && game.start_date instanceof Date && formatDate(game.start_date)}</td>
                  </ClickableTableRow>
                </tbody>
              )}
            </table>
          </div>
          {gameList && gameList.length > 0 && <p>Showing all {gameList?.length} games</p>}
        </section>
      </main>
    </>
  );
}

const getGames = (response: ResponseType) => {
  let games: Game[] = [];

  if (response && response.data) {
    for (let i = 0; i < response.data.length; i++) {
      if (response.data[i]) {
        const game = new Game(response.data[i]);
        games.push(game);
      }
    }

    games.sort((game1, game2) => {
      const date1 = new Date(game1.creation_date);
      const date2 = new Date(game2.creation_date);
      return date2.getTime() - date1.getTime();
    });
  }
  return games;
}

export default GamesPage;

export async function getServerSideProps(context: GetServerSidePropsContext) {

  const { ssrAccessToken, ssrRefreshToken, ssrUsername } = getInitialCookieData(context);
  
  const response = await request('GET', 'games/', ssrAccessToken, ssrRefreshToken);

  const games = getGames(response).map((game) => JSON.stringify(game));

  return {
    props: {
      ssrEnabled: true,
      ssrAccessToken: ssrAccessToken,
      ssrRefreshToken: ssrRefreshToken,
      ssrUsername: ssrUsername,
      initialGameList: games
    },
  };
}
