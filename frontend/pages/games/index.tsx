import { useState, useCallback } from 'react';
import { GetServerSidePropsContext } from 'next';
import Head from 'next/head';
import Link from 'next/link';

import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { DataGrid, GridColDef, GridRenderCellParams, GridValueGetterParams } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';

import { useAuthContext } from '@/contexts/AuthContext';
import request from "@/functions/request";
import Game from "@/classes/Game";
import getInitialCookieData from '@/functions/cookies';
import Breadcrumb from '@/components/Breadcrumb';
import ElapsedTime from '@/components/ElapsedTime';
import PageError from '@/components/PageError';
import formatDate from '@/functions/date';
import { deserializeToInstances } from '@/functions/serialize';
import GameParticipant from '@/classes/GameParticipant';

interface BrowseGamesPageProps {
  clientTimezone: string
  authFailure: boolean
  initialGames: string
  initialGameParticipants: string
}

// The "Browse Games" page component
const BrowseGamesPage = (props: BrowseGamesPageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();
  const [refreshPending, setRefreshPending] = useState<boolean>(false);
  const [games, setGames] = useState<Game[]>(() => {
    if (props.initialGames) {
      return deserializeToInstances<Game>(Game, props.initialGames)
    }
    return []
  });
  const [gameParticipants, setGameParticipants] = useState<GameParticipant[]>(() => {
    if (props.initialGameParticipants) {
      return deserializeToInstances<GameParticipant>(GameParticipant, props.initialGameParticipants)
    }
    return []
  });
  const [timeResetKey, setTimeResetKey] = useState(games.length == 0 ? 0 : 1);

  // Gets the participant count for a rows participant column
  const getParticipantCount = useCallback((params: GridValueGetterParams) => {
    return gameParticipants.filter(
      (gameParticipant: GameParticipant) => {
        return gameParticipant.game == params.row.id
      }
    ).length
  }, [gameParticipants])

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Name',
      minWidth: 150,
      flex: 2,
      hideable: false
    },
    {
      field: 'host',
      headerName: 'Host',
      minWidth: 150,
      flex: 2,
      valueGetter: (params: GridValueGetterParams) => params.row.host.username
    },
    {
      field: 'creationDate',
      headerName: 'Creation Date',
      minWidth: 150,
      flex: 1,
      valueGetter: (params: GridValueGetterParams) => formatDate(params.row.creation_date, props.clientTimezone)
    },
    {
      field: 'participants',
      headerName: 'Participants',
      minWidth: 120,
      type: 'number',
      headerAlign: 'left',
      valueGetter: (params: GridValueGetterParams) => getParticipantCount(params)
    },
    {
      field: 'viewButton',
      headerName: '',
      minWidth: 120,
      sortable: false,
      hideable: false,
      align: 'right',
      headerAlign: 'right',
      disableColumnMenu: true,
      renderCell: (params: GridRenderCellParams) => {
        return <Button LinkComponent={Link} href={`/games/${params.row.id}`}>View</Button>
      },
    }
  ];

  const fetchGames = useCallback(async () => {
    const response = await request('GET', 'games/?prefetch_user', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      setGames(deserializeToInstances<Game>(Game, response.data));
    } else {
      setGames([]);
    }
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUser]);

  const fetchGameParticipants = useCallback(async () => {
    const response = await request('GET', 'game-participants/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    if (response.status === 200) {
      setGameParticipants(deserializeToInstances<GameParticipant>(GameParticipant, response.data));
    } else {
      setGameParticipants([]);
    }
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Refresh the game list
  const refreshGames = useCallback(async () => {
    fetchGames()
    fetchGameParticipants()
    setTimeResetKey(e => e + 1);
  }, [fetchGames, fetchGameParticipants, setTimeResetKey]);

  // Process a click of the submission button
  const handleRefresh = async () => {
    setRefreshPending(true);
    await refreshGames();
    setRefreshPending(false);
  }

  // Sign out if authentication failed on the server
  if (props.authFailure) {
    setAccessToken('')
    setRefreshToken('')
    setUser(null)
  }

  // Render page error if user is not signed in
  if (user === null || props.authFailure) {
    return <PageError statusCode={401} />;
  }

  return (
    <>
      <Head>
        <title>Browse Games | Republic of Rome Online</title>
      </Head>
      <main className="standard-page">
        <Breadcrumb />

        <section>
          <Stack spacing={2} marginBottom={2} direction={{ md: "row" }} justifyContent={{ md: "space-between" }} gap={{ xs: 2 }}>
            <h2 style={{margin: "0"}}>Browse Games</h2>
            
            <Stack spacing={{ xs: 2 }} direction={{ xs: "column-reverse", sm: "row" }} justifyContent={{ sm: "end" }} alignItems={{ sm: "center"}}>
              {timeResetKey !== 0 && !refreshPending &&
                <p style={{textAlign: 'center', margin: 0}}>
                  Last updated <ElapsedTime resetKey={timeResetKey} />
                </p>
              }
              {refreshPending && <p style={{textAlign: 'center', margin: 0, color: "var(--foreground-color-muted)"}}>Loading...</p>}
              <Button variant="outlined" onClick={handleRefresh}>Refresh</Button>
              <Button variant="contained" LinkComponent={Link} href="/games/new">Create Game</Button>
            </Stack>
          </Stack>
        </section>
        
        <section>
          <Card>
            <Box sx={{ width: '100%' }}>
              <DataGrid
                rows={games}
                columns={columns}
                initialState={{
                  pagination: {
                    paginationModel: {
                      pageSize: 10,
                    },
                  },
                }}
                pageSizeOptions={[10, 20, 30]}
                disableRowSelectionOnClick
              />
            </Box>
          </Card>
        </section>
      </main>
    </>
  );
}

export default BrowseGamesPage;

// The games and participants are retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {

  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context)
  
  // Asynchronously retrieve games and game participants
  const gamesRequest = request('GET', 'games/?prefetch_user', clientAccessToken, clientRefreshToken)
  const gameParticipantsRequest = request('GET', 'game-participants/', clientAccessToken, clientRefreshToken)
  const [gamesResponse, gameParticipantsResponse] = await Promise.all([gamesRequest, gameParticipantsRequest]);

  // Track whether there has been an authentication failure due to bad credentials
  let authFailure: boolean = false

  // Ensure that game and participant responses are OK before getting data
  let gamesJSON = null
  let gameParticipantsJSON = null
  if (gamesResponse.status === 200 && gameParticipantsResponse.status === 200) {
    gamesJSON = gamesResponse.data
    gameParticipantsJSON = gameParticipantsResponse.data
  } else if (gamesResponse.status === 401 || gameParticipantsResponse.status === 40) {
    authFailure = true
  }

  return {
    props: {
      ssrEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      authFailure: authFailure,
      initialGames: gamesJSON,
      initialGameParticipants: gameParticipantsJSON
    },
  }
}
