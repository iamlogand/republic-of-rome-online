import { useEffect, useState, useCallback } from 'react';
import { GetServerSidePropsContext } from 'next';
import Head from 'next/head';
import Link from 'next/link';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

import { useAuthContext } from '@/contexts/AuthContext';
import request, { ResponseType } from "@/functions/request"
import formatDate from '@/functions/date';
import Game from "@/classes/Game"
import getInitialCookieData from '@/functions/cookies';
import { useModalContext } from '@/contexts/ModalContext';
import ClickableTableRow from '@/components/LinkedTableRow';
import Breadcrumb from '@/components/Breadcrumb';
import ElapsedTime from '@/components/ElapsedTime';
import PageError from '@/components/PageError';

interface GamesPageProps {
  initialGameList: string[];
  clientTimezone: string;
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

        <section>
          <Stack spacing={2} marginBottom={2} direction={{ md: "row" }} justifyContent={{ md: "space-between" }}>
            <h2 style={{margin: "10px 0"}}>Browse Games</h2>
            
            <Stack spacing={{ xs: 2 }} direction={{ xs: "column-reverse", sm: "row" }} justifyContent={{ sm: "end" }} alignItems={{ sm: "center"}}>
              {timeResetKey != 0 &&
                <p style={{textAlign: 'center', margin: 0}}>
                  Last updated <ElapsedTime resetKey={timeResetKey} />
                </p>
              }
              <Button variant="outlined" onClick={handleRefresh}>Refresh</Button>
              <Button variant="contained" LinkComponent={Link} href="/games/new">Create Game</Button>
            </Stack>
          </Stack>
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
                  <th>Participants</th>
                </tr>
              </thead>

              {gameList && gameList.length > 0 && gameList.map((game, index) =>
                <tbody key={index}>
                  <ClickableTableRow href={'/games/' + game.id}>
                    <td className='no-wrap-ellipsis'>{game.name}</td>
                    <td className='no-wrap-ellipsis'>{game.owner == username ? <b>You</b> : game.owner}</td>
                    <td>{game.creation_date && game.creation_date instanceof Date && formatDate(game.creation_date, props.clientTimezone)}</td>
                    <td>{game.start_date && game.start_date instanceof Date && formatDate(game.start_date, props.clientTimezone)}</td>
                    <td>{game.participants && game.participants.length}</td>
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

  const { clientAccessToken, clientRefreshToken, clientUsername, clientTimezone } = getInitialCookieData(context);
  
  const response = await request('GET', 'games/', clientAccessToken, clientRefreshToken);

  const games = getGames(response).map((game) => JSON.stringify(game));

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUsername: clientUsername,
      clientTimezone: clientTimezone,
      initialGameList: games
    },
  };
}
