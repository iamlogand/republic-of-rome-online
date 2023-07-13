import { useEffect, useState, useCallback } from 'react';
import { GetServerSidePropsContext } from 'next';
import Head from 'next/head';
import Link from 'next/link';

import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { DataGrid, GridColDef, GridRenderCellParams, GridValueGetterParams } from '@mui/x-data-grid';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';

import { useAuthContext } from '@/contexts/AuthContext';
import request, { ResponseType } from "@/functions/request";
import Game from "@/classes/Game";
import getInitialCookieData from '@/functions/cookies';
import { useModalContext } from '@/contexts/ModalContext';
import Breadcrumb from '@/components/Breadcrumb';
import ElapsedTime from '@/components/ElapsedTime';
import PageError from '@/components/PageError';
import formatDate from '@/functions/date';
import router from 'next/router';

interface GamesPageProps {
  initialGameList: string[];
  clientTimezone: string;
}

/**
 * The component for the game list page
 */
const GamesPage = (props: GamesPageProps) => {
  const { accessToken, refreshToken, user, setAccessToken, setRefreshToken, setUser } = useAuthContext();
  const [refreshPending, setRefreshPending] = useState<boolean>(false);
  const [gameList, setGameList] = useState<Game[]>(props.initialGameList.map((gameString) => new Game(JSON.parse(gameString))));
  const [timeResetKey, setTimeResetKey] = useState(gameList.length == 0 ? 0 : 1);

  const columns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Name',
      minWidth: 150,
      flex: 3,
      hideable: false
    },
    {
      field: 'host',
      headerName: 'Host',
      minWidth: 150,
      flex: 2
    },
    {
      field: 'creationDate',
      headerName: 'Creation Date',
      minWidth: 150,
      valueGetter: (params: GridValueGetterParams) => formatDate(params.row.creation_date, props.clientTimezone)
    },
    {
      field: 'startDate',
      headerName: 'Start Date',
      minWidth: 150,
      valueGetter: (params: GridValueGetterParams) => 
        params.row.start_date ?
        formatDate(params.row.start_date, props.clientTimezone) :
        ""
    },
    {
      field: 'participants',
      headerName: 'Parties',
      minWidth: 60,
      type: 'number',
      headerAlign: 'left',
      valueGetter: (params: GridValueGetterParams) => params.row.participants.length
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

  // Refresh the game list
  const refreshGames = useCallback(async () => {
    const response = await request('GET', 'games/', accessToken, refreshToken, setAccessToken, setRefreshToken, setUser);
    const games = getGames(response);
    setGameList(games);
    setTimeResetKey(e => e + 1);
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUser, setTimeResetKey]);

  // Process a click of the submission button
  const handleRefresh = async () => {
    setRefreshPending(true);
    await refreshGames();
    setRefreshPending(false);
  }

  // Render page error if user is not signed in
  if (user === null) {
    return <PageError statusCode={401} />;
  }

  return (
    <>
      <Head>
        <title>Browse Games | Republic of Rome Online</title>
      </Head>
      <main>
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
                rows={gameList}
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

  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } = getInitialCookieData(context)
  
  const response = await request('GET', 'games/', clientAccessToken, clientRefreshToken)

  const games = getGames(response).map((game) => JSON.stringify(game))

  return {
    props: {
      clientEnabled: true,
      clientAccessToken: clientAccessToken,
      clientRefreshToken: clientRefreshToken,
      clientUser: clientUser,
      clientTimezone: clientTimezone,
      initialGameList: games
    },
  }
}
