import { useEffect, useRef, useState } from "react"
import debounce from "lodash/debounce"
import { Button, IconButton } from "@mui/material"
import EastIcon from "@mui/icons-material/East"

import Collection from "@/classes/Collection"
import Action from "@/classes/Action"
import Actions from "@/data/actions.json"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import { useAuthContext } from "@/contexts/AuthContext"
import ActionDialog from "@/components/actionDialogs/ActionDialog"
import ActionsType from "@/types/actions"
import Faction from "@/classes/Faction"
import ActionLog from "@/classes/ActionLog"
import Notification from "@/components/actionLogs/ActionLog"
import FactionLink from "@/components/FactionLink"
import { ExpandCircleDown } from "@mui/icons-material"

const typedActions: ActionsType = Actions

const SEQUENTIAL_PHASES = ["Forum"]

interface ProgressSectionProps {
  latestActions: Collection<Action>
  notifications: Collection<ActionLog>
}

// Progress section showing who players are waiting for
const ProgressSection = ({
  latestActions,
  notifications,
}: ProgressSectionProps) => {
  const { user } = useAuthContext()
  const { latestPhase, allPlayers, allFactions } = useGameContext()
  const [thisFactionsPendingActions, setThisFactionsPendingActions] = useState<
    Collection<Action>
  >(new Collection<Action>())
  const [dialogOpen, setDialogOpen] = useState<boolean>(false)
  const [faction, setFaction] = useState<Faction | null>(null)
  const notificationListRef = useRef<HTMLDivElement>(null)
  const [initiateScrollDown, setInitiateScrollDown] = useState(false)
  const [isNearBottom, setIsNearBottom] = useState(true)

  // Update faction
  useEffect(() => {
    const player = allPlayers.asArray.find((p) => p.user?.id === user?.id)
    setFaction(allFactions.asArray.find((f) => f.player === player?.id) ?? null)
  }, [user, allPlayers, allFactions, setFaction])

  // Update actions
  useEffect(() => {
    setThisFactionsPendingActions(
      new Collection<Action>(
        latestActions?.asArray.filter(
          (a) => a.faction === faction?.id && a.completed === false
        ) ?? []
      )
    )
  }, [latestActions, faction, setThisFactionsPendingActions])

  useEffect(() => {
    const scrollableDiv = notificationListRef.current
    if (scrollableDiv === null) return

    const handleScroll = () => {
      const isNearBottom =
        scrollableDiv.scrollHeight -
          scrollableDiv.scrollTop -
          scrollableDiv.clientHeight <
        3
      setIsNearBottom(isNearBottom)
    }

    scrollableDiv.addEventListener("scroll", handleScroll)
    return () => scrollableDiv.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    if (isNearBottom) setInitiateScrollDown(true)
  }, [notifications.allIds.length, isNearBottom])

  const scrollToBottom = (element: HTMLDivElement) => {
    element.scrollTo({
      top: element.scrollHeight,
      behavior: "smooth",
    })
  }

  useEffect(() => {
    const scrollableDiv = notificationListRef.current
    if (scrollableDiv === null || !initiateScrollDown) return

    scrollToBottom(scrollableDiv)
    setInitiateScrollDown(false)
  }, [initiateScrollDown])

  if (thisFactionsPendingActions) {
    const requiredAction = thisFactionsPendingActions.asArray.find(
      (a) => a.required === true
    )

    let waitingForDesc = <span></span>
    const pendingActions = latestActions.asArray.filter(
      (a) => a.completed === false
    )
    const firstPotentialAction = pendingActions[0]
    if (pendingActions.length > 1) {
      waitingForDesc = (
        <span>
          Waiting for {pendingActions.length} factions to{" "}
          {typedActions[firstPotentialAction.type]["sentence"]}
        </span>
      )
    } else if (pendingActions.length === 1) {
      const onlyPendingFaction = allFactions.asArray.find(
        (f) => f.id === firstPotentialAction.faction
      )
      if (onlyPendingFaction)
        waitingForDesc = (
          <span>
            Waiting for{" "}
            {faction === onlyPendingFaction ? (
              <span>you</span>
            ) : (
              <FactionLink faction={onlyPendingFaction} />
            )}{" "}
            to {typedActions[firstPotentialAction.type]["sentence"]}
          </span>
        )
    }

    return (
      <div className="box-border h-full px-4 py-2 flex flex-col gap-4">
        <div className="flex-1 flex flex-col overflow-y-auto relative">
          <h3 className="leading-lg m-2 ml-2 text-base text-stone-600">
            Notifications
          </h3>
          {!isNearBottom && (
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
              <IconButton
                onClick={() => setInitiateScrollDown(true)}
                size="large"
              >
                <ExpandCircleDown fontSize="inherit" />
              </IconButton>
            </div>
          )}
          <div
            ref={notificationListRef}
            className="h-full overflow-y-auto p-2 bg-white border border-solid border-stone-200 rounded shadow-inner flex flex-col gap-2 scroll-smooth"
          >
            {notifications &&
              notifications.asArray
                .sort((a, b) => a.index - b.index)
                .map((notification) => (
                  <Notification
                    key={notification.id}
                    notification={notification}
                  />
                ))}
          </div>
        </div>
        <div className="flex flex-col gap-2">
          <h3 className="leading-none m-0 ml-2 text-base text-stone-600">
            Actions
          </h3>
          <div className="p-2 bg-white border border-solid border-stone-200 rounded shadow-inner flex flex-col gap-3 items-center">
            <p className="text-center">{waitingForDesc}</p>
            <div className="h-full flex gap-3 justify-center">
              {allFactions.asArray.map((faction, index) => {
                const potential = latestActions.asArray.some(
                  (a) => a.faction === faction.id && a.completed === false
                )
                return (
                  <div
                    key={index}
                    className="mt-1 flex items-start justify-center gap-3"
                  >
                    {index !== 0 &&
                      SEQUENTIAL_PHASES.some(
                        (name) => name === latestPhase?.name
                      ) && (
                        <div className="self-start w-1 h-6 relative">
                          <div className="absolute bottom-1/2 right-1/2 translate-x-1/2 translate-y-1/2">
                            <EastIcon fontSize="small" />
                          </div>
                        </div>
                      )}
                    <div className="w-6 h-6 flex items-start justify-center">
                      <FactionIcon
                        faction={faction}
                        size={!potential ? 18 : 24}
                        muted={!potential}
                        selectable
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
          <div className="mt-0 mb-2">
            {thisFactionsPendingActions.allIds.length > 0 && requiredAction ? (
              <div className="flex flex-col">
                <Button variant="contained" onClick={() => setDialogOpen(true)}>
                  {typedActions[requiredAction.type]["title"]}
                </Button>
                <ActionDialog
                  actions={thisFactionsPendingActions}
                  open={dialogOpen}
                  setOpen={setDialogOpen}
                  onClose={() => setDialogOpen(false)}
                />
              </div>
            ) : (
              <div className="flex flex-col">
                {faction && (
                  <Button variant="contained" disabled>
                    Waiting for others
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  } else {
    return null
  }
}

export default ProgressSection
