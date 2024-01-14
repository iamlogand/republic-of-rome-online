import {
  Dispatch,
  SetStateAction,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react"
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

  const fetchAndSetInstance = useCallback(
    <Entity extends { id: number }>(
      EntityType: EntityConstructor<Entity>,
      setEntity: Dispatch<SetStateAction<Entity | null>>,
      url: string
    ) => {
      fetchData(
        url,
        (data: any) => {
          const deserializedInstance = new EntityType(data.id ? data : data[0])
          setEntity(deserializedInstance)
        },
        () => {}
      )
    },
    [fetchData]
  )

  type EntityConstructor<Entity> = new (data: any) => Entity

  const fetchAndSetCollection = useCallback(
    <Entity extends { id: number }>(
      EntityType: EntityConstructor<Entity>,
      setEntity: Dispatch<SetStateAction<Collection<Entity>>>,
      url: string
    ) => {
      fetchData(
        url,
        (data: any) => {
          const deserializedInstances = data.map(
            (item: any) => new EntityType(item)
          )
          setEntity(new Collection<Entity>(deserializedInstances))
        },
        () => {
          setEntity(new Collection<Entity>())
        }
      )
    },
    [fetchData]
  )

  const fetchGame = useCallback(() => {
    const url = `games/${props.gameId}/?prefetch_user`
    fetchAndSetInstance(Game, setGame, url)
  }, [props.gameId, setGame, fetchAndSetInstance])

  const fetchPlayers = useCallback(async () => {
    const url = `players/?game=${props.gameId}&prefetch_user`
    fetchAndSetCollection(Player, setAllPlayers, url)
  }, [props.gameId, setAllPlayers, fetchAndSetCollection])

  const fetchFactions = useCallback(async () => {
    const url = `factions/?game=${props.gameId}`
    fetchAndSetCollection(Faction, setAllFactions, url)
  }, [props.gameId, setAllFactions, fetchAndSetCollection])

  const fetchSenators = useCallback(async () => {
    const url = `senators/?game=${props.gameId}`
    fetchAndSetCollection(Senator, setAllSenators, url)
  }, [props.gameId, setAllSenators, fetchAndSetCollection])

  const fetchTitles = useCallback(async () => {
    const url = `titles/?game=${props.gameId}&relevant`
    fetchAndSetCollection(Title, setAllTitles, url)
  }, [props.gameId, setAllTitles, fetchAndSetCollection])

  const fetchLatestTurn = useCallback(async () => {
    const url = `turns/?game=${props.gameId}&ordering=-index&limit=1`
    fetchAndSetInstance(Turn, setLatestTurn, url)
  }, [props.gameId, setLatestTurn, fetchAndSetInstance])

  const fetchLatestPhase = useCallback(async () => {
    const url = `phases/?game=${props.gameId}&ordering=latest&limit=1`
    fetchAndSetInstance(Phase, setLatestPhase, url)
  }, [props.gameId, setLatestPhase, fetchAndSetInstance])

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

  // Function to handle instance updates
  const handleInstanceUpdate = useCallback(
    () =>
      <Entity extends { id: number }>(
        setFunction: Dispatch<SetStateAction<Entity | null>>,
        EntityType: EntityConstructor<Entity>,
        message: any
      ) => {
        if (message?.operation == "create") {
          const instance = deserializeToInstance<Entity>(
            EntityType,
            message.instance.data
          )
          if (instance) {
            setFunction(instance)
          }
        } else if (message?.operation == "destroy") {
          setFunction(null)
        }
      },
    []
  )

  // Function to handle collection updates
  const handleCollectionUpdate = useCallback(
    () =>
      <Entity extends { id: number }>(
        setFunction: Dispatch<SetStateAction<Collection<Entity>>>,
        EntityType: EntityConstructor<Entity>,
        message: any
      ) => {
        if (message?.operation == "create") {
          const instance = deserializeToInstance<Entity>(
            EntityType,
            message.instance.data
          )
          if (instance) {
            setFunction((instances) => {
              if (instances.allIds.includes(instance.id)) {
                instances = instances.remove(instance.id)
              }
              return instances.add(instance)
            })
          }
        } else if (message?.operation == "destroy") {
          setFunction((instances) => instances.remove(message.instance.id))
        }
      },
    []
  )

  type ClassUpdateMap = {
    [key: string]: [
      React.Dispatch<React.SetStateAction<any>>,
      new (data: any) => any,
      (
        setFunction: React.Dispatch<React.SetStateAction<any>>,
        ClassType: new (data: any) => any,
        message: any
      ) => void
    ]
  }

  const classUpdateMap: ClassUpdateMap = useMemo(
    () => ({
      turn: [setLatestTurn, Turn, handleInstanceUpdate],
      phase: [setLatestPhase, Phase, handleInstanceUpdate],
      step: [setLatestStep, Step, handleInstanceUpdate],
      faction: [setAllFactions, Faction, handleCollectionUpdate],
      senator: [setAllSenators, Senator, handleCollectionUpdate],
      action: [setLatestActions, Action, handleCollectionUpdate],
      title: [setAllTitles, Title, handleCollectionUpdate],
      action_log: [setNotifications, ActionLog, handleCollectionUpdate],
      senator_action_log: [
        setSenatorActionLogs,
        SenatorActionLog,
        handleCollectionUpdate,
      ],
    }),
    [
      handleCollectionUpdate,
      handleInstanceUpdate,
      setLatestTurn,
      setLatestPhase,
      setLatestStep,
      setLatestActions,
      setAllFactions,
      setAllTitles,
      setAllSenators,
      setNotifications,
      setSenatorActionLogs,
    ]
  )

  // Read WebSocket messages and use payloads to update state
  useEffect(() => {
    if (lastMessage?.data) {
      const deserializedData = JSON.parse(lastMessage.data)
      if (deserializedData && deserializedData.length > 0) {
        for (const message of deserializedData) {
          if (
            message?.operation == "create" ||
            message?.operation == "destroy"
          ) {
            const [setFunction, ClassType, handleUpdate] =
              classUpdateMap[
                message.instance.class as keyof typeof classUpdateMap
              ]
            if (setFunction && ClassType && handleUpdate) {
              handleUpdate(setFunction, ClassType, message)
            }
          }
        }
      }
    }
  }, [
    lastMessage,
    game?.id,
    classUpdateMap,
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
