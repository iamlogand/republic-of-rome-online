import { useState, useCallback, useEffect } from "react"
import { GetServerSidePropsContext } from "next"
import Head from "next/head"
import Link from "next/link"

import Button from "@mui/material/Button"
import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid"

import { useCookieContext } from "@/contexts/CookieContext"
import request from "@/functions/request"
import Game from "@/classes/Game"
import getInitialCookieData from "@/functions/cookies"
import Breadcrumb from "@/components/Breadcrumb"
import ElapsedTime from "@/components/ElapsedTime"
import PageError from "@/components/PageError"
import formatDate from "@/functions/date"
import { deserializeToInstances } from "@/functions/serialize"
import Player from "@/classes/Player"

interface BrowseGamesPageProps {
  clientTimezone: string
  authFailure: boolean
  initialGames: string
  initialPlayers: string
}

// The "Browse Games" page component
const BrowseGamesPage = (props: BrowseGamesPageProps) => {
  const {
    accessToken,
    refreshToken,
    user,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useCookieContext()
  const [refreshPending, setRefreshPending] = useState<boolean>(false)
  const [games, setGames] = useState<Game[]>(() => {
    if (props.initialGames) {
      return deserializeToInstances<Game>(Game, props.initialGames)
    }
    return []
  })
  const [players, setPlayers] = useState<Player[]>(() => {
    if (props.initialPlayers) {
      return deserializeToInstances<Player>(Player, props.initialPlayers)
    }
    return []
  })
  const [timeResetKey, setTimeResetKey] = useState(games.length == 0 ? 0 : 1)

  const columns: GridColDef[] = [
    {
      field: "name",
      headerName: "Name",
      minWidth: 150,
      flex: 2,
      hideable: false,
    },
    {
      field: "host",
      headerName: "Host",
      minWidth: 150,
      flex: 2,
      valueGetter: (_, row) => row.host.username,
    },
    {
      field: "creationDate",
      headerName: "Creation Date",
      minWidth: 150,
      flex: 1,
      valueGetter: (_, row) =>
        formatDate(row.creation_date, props.clientTimezone),
    },
    {
      field: "players",
      headerName: "Players",
      minWidth: 120,
      type: "number",
      headerAlign: "left",
      valueGetter: (_, row) =>
        players.filter((player: Player) => player.game == row.id).length,
    },
    {
      field: "viewButton",
      headerName: "",
      minWidth: 120,
      sortable: false,
      hideable: false,
      align: "right",
      headerAlign: "right",
      disableColumnMenu: true,
      renderCell: (params: GridRenderCellParams) => {
        return (
          <Button LinkComponent={Link} href={`/games/${params.row.id}`}>
            View
          </Button>
        )
      },
    },
  ]

  const fetchGames = useCallback(async () => {
    const response = await request(
      "GET",
      "games/?prefetch_user",
      accessToken,
      refreshToken,
      setAccessToken,
      setRefreshToken,
      setUser
    )
    if (response.status === 200) {
      setGames(deserializeToInstances<Game>(Game, response.data))
    } else {
      setGames([])
    }
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  const fetchPlayers = useCallback(async () => {
    const response = await request(
      "GET",
      "players/",
      accessToken,
      refreshToken,
      setAccessToken,
      setRefreshToken,
      setUser
    )
    if (response.status === 200) {
      setPlayers(deserializeToInstances<Player>(Player, response.data))
    } else {
      setPlayers([])
    }
  }, [accessToken, refreshToken, setAccessToken, setRefreshToken, setUser])

  // Refresh the game list
  const refreshGames = useCallback(async () => {
    const requests = [fetchGames(), fetchPlayers()]
    await Promise.all(requests)
    setTimeResetKey((e) => e + 1)
  }, [fetchGames, fetchPlayers, setTimeResetKey])

  // Process a click of the submission button
  const handleRefresh = async () => {
    setRefreshPending(true)
    await refreshGames()
    setRefreshPending(false)
  }

  // Sign out if authentication failed on the server
  useEffect(() => {
    if (props.authFailure) {
      setAccessToken("")
      setRefreshToken("")
      setUser(null)
    }
  }, [props.authFailure, setAccessToken, setRefreshToken, setUser])

  // Render page error if user is not signed in
  if (user === null || props.authFailure) {
    return <PageError statusCode={401} />
  }

  return (
    <>
      <Head>
        <title>Browse Games | Republic of Rome Online</title>
      </Head>
      <main className="standard-page px-8 mb-8">
        <Breadcrumb />

        <section>
          <div className="pt-0 pb-4 flex flex-col sm:flex-row gap-4 justify-between">
            <h2 className="font-semibold text-xl tracking-tight">
              Browse Games
            </h2>

            <div className="self-end flex items-center gap-x-4 gap-y-2 flex-wrap">
              {timeResetKey !== 0 && !refreshPending && (
                <p style={{ textAlign: "center", margin: 0 }}>
                  Last updated <ElapsedTime resetKey={timeResetKey} />
                </p>
              )}
              {refreshPending && (
                <p
                  style={{
                    textAlign: "center",
                    margin: 0,
                  }}
                >
                  Loading...
                </p>
              )}
              <Button onClick={handleRefresh}>Refresh</Button>
              <Button variant="outlined" LinkComponent={Link} href="/games/new">
                Create Game
              </Button>
            </div>
          </div>
        </section>

        <section>
          <div className="bg-white dark:bg-neutral-700 rounded">
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
          </div>
        </section>
      </main>
    </>
  )
}

export default BrowseGamesPage

// The games and players are retrieved by the frontend server
export async function getServerSideProps(context: GetServerSidePropsContext) {
  // Get client cookie data from the page request
  const { clientAccessToken, clientRefreshToken, clientUser, clientTimezone } =
    getInitialCookieData(context)

  // Asynchronously retrieve games and game players
  const gamesRequest = request(
    "GET",
    "games/?prefetch_user",
    clientAccessToken,
    clientRefreshToken
  )
  const playersRequest = request(
    "GET",
    "players/",
    clientAccessToken,
    clientRefreshToken
  )
  const [gamesResponse, playersResponse] = await Promise.all([
    gamesRequest,
    playersRequest,
  ])

  // Track whether there has been an authentication failure due to bad credentials
  let authFailure: boolean = false

  // Ensure that game and player responses are OK before getting data
  let gamesJSON = null
  let playersJSON = null
  if (gamesResponse.status === 200 && playersResponse.status === 200) {
    gamesJSON = gamesResponse.data
    playersJSON = playersResponse.data
  } else if (gamesResponse.status === 401 || playersResponse.status === 40) {
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
      initialPlayers: playersJSON,
    },
  }
}
