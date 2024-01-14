import { useCallback, useEffect, useState } from "react"
import Head from "next/head"
import useWebSocket from "react-use-websocket"

import Tabs from "@mui/material/Tabs"
import Tab from "@mui/material/Tab"
import Box from "@mui/material/Box"
import CircularProgress from "@mui/material/CircularProgress"

import { useGameContext } from "@/contexts/GameContext"
import Game from "@/classes/Game"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import Senator from "@/classes/Senator"
import Title from "@/classes/Title"
import PageError from "@/components/PageError"
import request from "@/functions/request"
import { useAuthContext } from "@/contexts/AuthContext"
import {
  deserializeToInstance,
  deserializeToInstances,
} from "@/functions/serialize"
import Collection from "@/classes/Collection"
import styles from "./GamePage.module.css"
import SenatorList from "@/components/SenatorList"
import FactionList from "@/components/FactionList"
import DetailSection from "@/components/detailSections/DetailSection"
import Turn from "@/classes/Turn"
import Phase from "@/classes/Phase"
import Step from "@/classes/Step"
import MetaSection from "@/components/MetaSection"
import Action from "@/classes/Action"
import ProgressSection from "@/components/ProgressSection"
import ActionLog from "@/classes/ActionLog"
import refreshAccessToken from "@/functions/tokens"
import SenatorActionLog from "@/classes/SenatorActionLog"

const webSocketURL: string = process.env.NEXT_PUBLIC_WS_URL ?? ""

// Props are passed here from the `GamePageWrapper`
export interface GamePageProps {
  clientTimezone: string
  gameId: string
  authFailure: boolean
  initialGame: string
  initialLatestSteps: string
}

// The game page component - the most important component in the frontend project.
// This would be an actual page if it wasn't wrapped by `GamePageWrapper`, which supplies `GameContext`
const GamePage = (props: GamePageProps) => {
  const {
    accessToken,
    refreshToken,
    user,
    setAccessToken,
    setRefreshToken,
    setUser,
  } = useAuthContext()
  const [syncingGameData, setSyncingGameData] = useState<boolean>(true)
  const [latestTokenRefreshDate, setLatestTokenRefreshDate] =
    useState<Date | null>(null)
  const [refreshingToken, setRefreshingToken] = useState<boolean>(false)

  // Game-specific state
  const {
    game,
    setGame,
    setLatestTurn,
    setLatestPhase,
    latestStep,
    setLatestStep,
    setAllPlayers,
    setAllFactions,
    setAllSenators,
    setAllTitles,
    setActionLogs,
    setSenatorActionLogs,
    notifications,
    setNotifications,
  } = useGameContext()
  const [latestActions, setLatestActions] = useState<Collection<Action>>(
    new Collection<Action>()
  )

  // Set game-specific state using initial data
  useEffect(() => {
    setGame(
      props.initialGame
        ? deserializeToInstance<Game>(Game, props.initialGame)
        : null
    )
  }, [props.initialGame, setGame])
  useEffect(() => {
    setLatestStep(
      props.initialLatestSteps
        ? deserializeToInstances<Step>(Step, props.initialLatestSteps)[0]
        : null
    )
  }, [props.initialLatestSteps, setLatestStep])

  // UI selections
  const [mainTab, setMainTab] = useState(0)
  const [mainSenatorListSort, setMainSenatorListSort] = useState<string>("")
  const [mainSenatorListGrouped, setMainSenatorListGrouped] =
    useState<boolean>(false)
  const [mainSenatorListFilterAlive, setMainSenatorListFilterAlive] =
    useState<boolean>(true)
  const [mainSenatorListFilterDead, setMainSenatorListFilterDead] =
    useState<boolean>(false)

  // Establish a WebSocket connection and provide a state containing the last message
  const { lastMessage } = useWebSocket(
    webSocketURL + `games/${props.gameId}/?token=${accessToken}`,
    {
      // On connection open perform a full sync
      onOpen: () => {
        console.log("WebSocket connection opened")
        fullSync()
        setLatestTokenRefreshDate(new Date())
      },

      // On connection close refresh the access token in case their access token has expired
      onClose: async () => {
        console.log("WebSocket connection closed (or failed to connect)")

        if (refreshingToken) return // Don't refresh access token if already being refreshed

        if (user === null) setSyncingGameData(false)

        // Refresh the access token if it hasn't been refreshed yet or is 1 hour old
        if (
          latestTokenRefreshDate === null ||
          (latestTokenRefreshDate &&
            latestTokenRefreshDate.getTime() < Date.now() - 1000 * 60 * 59)
        ) {
          console.log("Refreshing access token")
          setRefreshingToken(true)
          await refreshAccessToken(
            refreshToken,
            setAccessToken,
            setRefreshToken,
            setUser
          )
          setLatestTokenRefreshDate(new Date())
          setRefreshingToken(false)
        }
      },

      // Don't attempt to reconnect
      shouldReconnect: () => (user ? true : false),
    }
  )

  const fetchData = useCallback(
    async (
      url: string,
      onSuccess: (data: any) => void,
      onError: () => void
    ) => {
      const response = await request(
        "GET",
        url,
        accessToken,
        refreshToken,
        setAccessToken,
        setRefreshToken,
        setUser
      )
      if (response.status === 200) {
        onSuccess(response.data)
      } else {
        onError()
      }
    },
    [accessToken, refreshToken, setAccessToken, setRefreshToken, setUser]
  )

  // Fetch the game
  const fetchGame = useCallback(() => {
    const url = `games/${props.gameId}/?prefetch_user`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstance = deserializeToInstance<Game>(Game, data)
        setGame(deserializedInstance)
      },
      () => {}
    )
  }, [props.gameId, setGame, fetchData])

  // Fetch players
  const fetchPlayers = useCallback(async () => {
    const url = `players/?game=${props.gameId}&prefetch_user`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<Player>(
          Player,
          data
        )
        setAllPlayers(new Collection<Player>(deserializedInstances))
      },
      () => {
        setAllPlayers(new Collection<Player>())
      }
    )
  }, [props.gameId, setAllPlayers, fetchData])

  // Fetch factions
  const fetchFactions = useCallback(async () => {
    const url = `factions/?game=${props.gameId}`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<Faction>(
          Faction,
          data
        )
        setAllFactions(new Collection<Faction>(deserializedInstances))
      },
      () => {
        setAllFactions(new Collection<Faction>())
      }
    )
  }, [props.gameId, setAllFactions, fetchData])

  // Fetch senators
  const fetchSenators = useCallback(async () => {
    const url = `senators/?game=${props.gameId}`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<Senator>(
          Senator,
          data
        )
        setAllSenators(new Collection<Senator>(deserializedInstances))
      },
      () => {
        setAllSenators(new Collection<Senator>())
      }
    )
  }, [props.gameId, setAllSenators, fetchData])

  // Fetch titles
  const fetchTitles = useCallback(async () => {
    const url = `titles/?game=${props.gameId}&relevant`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<Title>(Title, data)
        setAllTitles(new Collection<Title>(deserializedInstances))
      },
      () => {
        setAllTitles(new Collection<Title>())
      }
    )
  }, [props.gameId, setAllTitles, fetchData])

  // Fetch the latest turn
  const fetchLatestTurn = useCallback(async () => {
    const url = `turns/?game=${props.gameId}&ordering=-index&limit=1`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstance = deserializeToInstance<Turn>(Turn, data[0])
        setLatestTurn(deserializedInstance)
      },
      () => {}
    )
  }, [props.gameId, setLatestTurn, fetchData])

  // Fetch the latest phase
  const fetchLatestPhase = useCallback(async () => {
    const url = `phases/?game=${props.gameId}&ordering=latest&limit=1`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstance = deserializeToInstance<Phase>(
          Phase,
          data[0]
        )
        setLatestPhase(deserializedInstance)
      },
      () => {}
    )
  }, [props.gameId, setLatestPhase, fetchData])

  // Fetch the latest step
  const fetchLatestStep = useCallback(async () => {
    const url = `steps/?game=${props.gameId}&ordering=-index&limit=1`
    let fetchedStep = null
    await fetchData(
      url,
      (data: any) => {
        const deserializedInstance = deserializeToInstance<Step>(Step, data[0])
        setLatestStep(deserializedInstance)
        fetchedStep = deserializedInstance
      },
      () => {}
    )
    return fetchedStep
  }, [props.gameId, setLatestStep, fetchData])

  // Fetch actions
  const fetchLatestActions = useCallback(
    async (step: Step) => {
      const url = `actions/?step=${step.id}`
      fetchData(
        url,
        (data: any) => {
          const deserializedInstances = deserializeToInstances<Action>(
            Action,
            data
          )
          setLatestActions(new Collection<Action>(deserializedInstances))
        },
        () => {
          setLatestActions(new Collection<Action>())
        }
      )
    },
    [setLatestActions, fetchData]
  )

  // Fetch notifications but uses fetchData()
  const fetchNotifications = useCallback(async () => {
    const minIndex = -10 // Fetch the last 10 notifications
    const maxIndex = -1
    const url = `action-logs/?game=${props.gameId}&min_index=${minIndex}&max_index=${maxIndex}`
    fetchData(
      url,
      (data: any) => {
        const deserializedInstances = deserializeToInstances<ActionLog>(
          ActionLog,
          data
        )
        setNotifications((notifications) => {
          // Merge the new notifications with the existing ones
          // Loop over each new notification and add it to the collection if it doesn't already exist
          for (const newInstance of deserializedInstances) {
            if (!notifications.allIds.includes(newInstance.id)) {
              notifications = notifications.add(newInstance)
            }
          }
          return notifications
        })
      },
      () => {
        setNotifications(new Collection<ActionLog>())
      }
    )
  }, [props.gameId, setNotifications, fetchData])

  // Fully synchronize all game data
  const fullSync = useCallback(async () => {
    if (user === null) {
      console.log("[Full Sync] skipped because user is not signed in")
      return // Don't attempt to sync if user is not signed in
    }
    if (refreshingToken) {
      console.log("[Full Sync] skipped because access token is being refreshed")
      return // Don't attempt to sync if access token is being refreshed
    }

    console.log("[Full Sync] started")
    const startTime = performance.now()

    setSyncingGameData(true)

    // Fetch game data
    const requestsBatch1 = [
      fetchLatestStep(), // Positional
      fetchGame(),
      fetchPlayers(),
      fetchFactions(),
      fetchSenators(),
      fetchTitles(),
      fetchLatestTurn(),
      fetchLatestPhase(),
      fetchNotifications(),
    ]
    const results = await Promise.all(requestsBatch1)
    const updatedLatestStep: Step | null = results[0] as Step | null

    if (updatedLatestStep) {
      const requestsBatch2 = [fetchLatestActions(updatedLatestStep)]
      await Promise.all(requestsBatch2)
    }

    setSyncingGameData(false)

    // Track time taken to sync
    const endTime = performance.now()
    const timeTaken = Math.round(endTime - startTime)

    console.log(`[Full Sync] completed in ${timeTaken}ms`)
  }, [
    refreshingToken,
    user,
    fetchGame,
    fetchPlayers,
    fetchFactions,
    fetchSenators,
    fetchTitles,
    fetchLatestTurn,
    fetchLatestPhase,
    fetchLatestStep,
    fetchLatestActions,
    fetchNotifications,
  ])

  // Read WebSocket messages and use payloads to update state
  useEffect(() => {
    if (lastMessage?.data) {
      const deserializedData = JSON.parse(lastMessage.data)
      if (deserializedData && deserializedData.length > 0) {
        for (const message of deserializedData) {
          // Latest turn updates
          if (message?.instance?.class === "turn") {
            // Update the latest turn
            if (message?.operation === "create") {
              const newInstance = deserializeToInstance<Turn>(
                Turn,
                message.instance.data
              )
              if (newInstance) {
                setLatestTurn(newInstance)
              }
            }
          }

          // Latest phase updates
          if (message?.instance?.class === "phase") {
            // Update the latest phase
            if (message?.operation === "create") {
              const newInstance = deserializeToInstance<Phase>(
                Phase,
                message.instance.data
              )
              if (newInstance) {
                setLatestPhase(newInstance)
              }
            }
          }

          // Latest step updates
          if (message?.instance?.class === "step") {
            // Update the latest step
            if (message?.operation === "create") {
              const newInstance = deserializeToInstance<Step>(
                Step,
                message.instance.data
              )
              if (newInstance) {
                setLatestStep(newInstance)
              }
            }
          }

          // Faction updates
          if (message?.instance?.class === "faction") {
            // Update a faction
            if (message?.operation === "create") {
              const updatedInstance = deserializeToInstance<Faction>(
                Faction,
                message.instance.data
              )
              if (updatedInstance) {
                setAllFactions((instances) => {
                  if (instances.allIds.includes(updatedInstance.id)) {
                    instances = instances.remove(updatedInstance.id)
                    return instances.add(updatedInstance)
                  } else {
                    return instances.add(updatedInstance)
                  }
                })
              }
            }
          }

          // Senator updates
          if (message?.instance?.class === "senator") {
            // Update a senator
            if (message?.operation === "create") {
              const updatedInstance = deserializeToInstance<Senator>(
                Senator,
                message.instance.data
              )
              if (updatedInstance) {
                setAllSenators((instances) => {
                  if (instances.allIds.includes(updatedInstance.id)) {
                    instances = instances.remove(updatedInstance.id)
                    return instances.add(updatedInstance)
                  } else {
                    return instances.add(updatedInstance)
                  }
                })
              }
            }
          }

          // Action updates
          if (message?.instance?.class === "action") {
            // Add an action
            if (message?.operation === "create") {
              const newInstance = deserializeToInstance<Action>(
                Action,
                message.instance.data
              )
              if (newInstance) {
                setLatestActions((instances) => {
                  if (instances.allIds.includes(newInstance.id)) {
                    instances = instances.remove(newInstance.id)
                    return instances.add(newInstance)
                  } else {
                    return instances.add(newInstance)
                  }
                })
              }
            }

            // Remove an action
            if (message?.operation === "destroy") {
              const idToRemove = message.instance.id
              setLatestActions((instances) => instances.remove(idToRemove))
            }
          }

          // Active title updates
          if (message?.instance?.class === "title") {
            // Add an active title
            if (message?.operation === "create") {
              const newInstance = deserializeToInstance<Title>(
                Title,
                message.instance.data
              )
              if (newInstance) {
                setAllTitles((instances) => {
                  if (instances.allIds.includes(newInstance.id)) {
                    instances = instances.remove(newInstance.id)
                    return instances.add(newInstance)
                  } else {
                    return instances.add(newInstance)
                  }
                })
              }
            }

            // Remove an active title
            if (message?.operation === "destroy") {
              const idToRemove = message.instance.id
              setAllTitles((instances) => instances.remove(idToRemove))
            }
          }

          // Action log updates
          if (message?.instance?.class === "action_log") {
            // Add an action log
            if (message?.operation === "create") {
              const newInstance = deserializeToInstance<ActionLog>(
                ActionLog,
                message.instance.data
              )
              // Before updating state, ensure that this instance has not already been added
              if (newInstance) {
                setNotifications((instances) => {
                  if (instances.allIds.includes(newInstance.id)) {
                    instances = instances.remove(newInstance.id)
                    return instances.add(newInstance)
                  } else {
                    return instances.add(newInstance)
                  }
                })
                setActionLogs((instances) => {
                  if (instances.allIds.includes(newInstance.id)) {
                    instances = instances.remove(newInstance.id)
                    return instances.add(newInstance)
                  } else {
                    return instances.add(newInstance)
                  }
                })
              }
            }
          }

          // Senator action log updates
          if (message?.instance?.class === "senator_action_log") {
            // Add a senator action log
            if (message?.operation === "create") {
              const newInstance = deserializeToInstance<SenatorActionLog>(
                SenatorActionLog,
                message.instance.data
              )
              // Before updating state, ensure that this instance has not already been added
              if (newInstance) {
                setSenatorActionLogs((instances) => {
                  if (instances.allIds.includes(newInstance.id)) {
                    instances = instances.remove(newInstance.id)
                    return instances.add(newInstance)
                  } else {
                    return instances.add(newInstance)
                  }
                })
              }
            }
          }
        }
      }
    }
  }, [
    lastMessage,
    game?.id,
    setLatestTurn,
    setLatestPhase,
    setLatestStep,
    setLatestActions,
    setAllFactions,
    setAllTitles,
    setAllSenators,
    setNotifications,
    setActionLogs,
    setSenatorActionLogs,
  ])

  // Remove old actions (i.e. actions from a step that is no longer the latest step)
  useEffect(() => {
    if (!latestStep) return
    if (latestActions.asArray.some((a) => a.step < latestStep?.id)) {
      setLatestActions(
        (actions) =>
          new Collection<Action>(
            actions.asArray.filter((a) => a.step === latestStep?.id)
          )
      )
    }
  }, [latestActions, latestStep])

  const handleMainTabChange = (
    event: React.SyntheticEvent,
    newValue: number
  ) => {
    setMainTab(newValue)
  }

  // Sign out if authentication failed on the server
  useEffect(() => {
    if (props.authFailure) {
      setAccessToken("")
      setRefreshToken("")
      setUser(null)
    }
  }, [props.authFailure, setAccessToken, setRefreshToken, setUser])

  // === Rendering ===

  if (!syncingGameData) {
    // Render page error if user is not signed in
    if (user === null || props.authFailure) {
      return <PageError statusCode={401} />
    }

    // Render page error if game doesn't exist or hasn't started yet
    if (game === null || game.start_date === null) {
      return <PageError statusCode={404} />
    }
  }

  // Render loading spinner if game data is being synchronized
  if (syncingGameData) {
    return (
      <>
        <Head>
          <title>Loading... | Republic of Rome Online</title>
        </Head>
        <main className={`${styles.play} p-2`}>
          <div className={styles.loading}>
            <span>Synchronizing{game && `: ${game.name}`}</span>
            <CircularProgress />
          </div>
        </main>
      </>
    )
  }

  return (
    <>
      <Head>
        <title>{`${game!.name} | Republic of Rome Online`}</title>
      </Head>
      <main
        className={`${styles.play} p-2 flex flex-col xl:overflow-auto xl:h-screen bg-stone-300`}
      >
        <div className="flex flex-col gap-2 xl:overflow-auto xl:grow">
          <MetaSection />
          <div className="flex flex-col gap-2 xl:flex-row xl:overflow-auto xl:flex-1">
            <div className="xl:overflow-auto xl:flex-1 xl:max-w-[540px]">
              <DetailSection />
            </div>
            <div className="xl:flex-1 xl:grow-[2] bg-stone-50 rounded shadow">
              <section className="flex flex-col h-[75vh] xl:h-full">
                <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
                  <Tabs
                    value={mainTab}
                    onChange={handleMainTabChange}
                    className="px-4"
                  >
                    <Tab label="Factions" />
                    <Tab label="Senators" />
                  </Tabs>
                </Box>
                {mainTab === 0 && <FactionList />}
                {mainTab === 1 && (
                  <div className="h-full box-border m-4">
                    <SenatorList
                      selectable
                      border
                      mainSenatorListSortState={[
                        mainSenatorListSort,
                        setMainSenatorListSort,
                      ]}
                      mainSenatorListGroupedState={[
                        mainSenatorListGrouped,
                        setMainSenatorListGrouped,
                      ]}
                      mainSenatorListFilterAliveState={[
                        mainSenatorListFilterAlive,
                        setMainSenatorListFilterAlive,
                      ]}
                      mainSenatorListFilterDeadState={[
                        mainSenatorListFilterDead,
                        setMainSenatorListFilterDead,
                      ]}
                    />
                  </div>
                )}
              </section>
            </div>
            <div className="xl:flex-1 xl:max-w-[540px] bg-stone-50 rounded shadow">
              <section className="flex flex-col h-[75vh] xl:h-full">
                <ProgressSection latestActions={latestActions} />
              </section>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}

export default GamePage
