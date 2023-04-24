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
import Link from 'next/link';
import PageError from '@/components/PageError';
import ClickableTableRow from '@/components/LinkedTableRow';
import router from 'next/router';

interface GamesPageProps {
  initialGameList: string[];
  pageStatus: number;
}

/**
 * The component for the game list page
 */
const GamesPage = (props: GamesPageProps) => {
  const { username, accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername } = useAuthContext();
  const { setModal } = useModalContext();
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [refreshPending, setRefreshPending] = useState<boolean>(false);
  const [gameList, setGameList] = useState<Game[]>(props.initialGameList.map((gameString) => new Game(JSON.parse(gameString))));
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const resetInterval = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  
    setElapsedSeconds(0);
    intervalRef.current = setInterval(() => {
      setElapsedSeconds((prevSeconds) => prevSeconds + 1);
    }, 1000);
  };

  // On game list update, start and reset an interval for the elapsed time message 
  useEffect(() => {
    resetInterval();
  }, [gameList])

  // Refresh the game list
  const refreshGames = useCallback(async () => {
    const response = await request('GET', 'games/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername);
    const games = getGames(response);
    setGameList(games);
    resetInterval();
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUsername]);

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
  if (username == '' || props.pageStatus == 401) {
    return <PageError statusCode={401} />;
  }

  const handleRowClick = (url: string) => {
    router.push(url);
  };

  return (
    <>
      <Head>
        <title>Browse Games - Republic of Rome Online</title>
      </Head>
      <main>
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
                  <th>Creation Date</th>
                  <th>Start Date</th>
                </tr>
              </thead>

              {gameList && gameList.length > 0 && gameList.map((game, index) =>
                <tbody key={index}>
                  <ClickableTableRow href={'/games/' + game.id}>
                    <span className='no-wrap-ellipsis'>{game.name}</span>
                    <span className='no-wrap-ellipsis'>{game.owner == username ? <b>You</b> : game.owner}</span>
                    <span>{game.creation_date && game.creation_date instanceof Date && formatDate(game.creation_date)}</span>
                    <span>{game.start_date && game.start_date instanceof Date && formatDate(game.start_date)}</span>
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
  const ssrStatus = response.status;

  const games = getGames(response).map((game) => JSON.stringify(game));

  return {
    props: {
      ssrEnabled: true,
      ssrAccessToken: ssrAccessToken,
      ssrRefreshToken: ssrRefreshToken,
      ssrUsername: ssrUsername,
      ssrStatus: ssrStatus,
      initialGameList: games
    },
  };
}
