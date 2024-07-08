import { useGameContext } from "@/contexts/GameContext"
import { ExpandCircleDown } from "@mui/icons-material"
import { Badge, IconButton } from "@mui/material"
import { useCallback, useEffect, useRef, useState } from "react"
import ActionLog from "@/components/ActionLog"
import ActionLogClass from "@/classes/ActionLog"
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft"

const NotificationList = () => {
  const { actionLogs, steps, phases, turns } = useGameContext()
  const notificationListRef = useRef<HTMLDivElement>(null)
  const [initiateScrollDown, setInitiateScrollDown] = useState(false)
  const [isNearBottom, setIsNearBottom] = useState(true)
  const [newNotifications, setNewNotifications] = useState(false)
  const [hideButton, setHideButton] = useState(false)
  const timeoutId = useRef<number | null>(null)
  const [sortedActionLogs, setSortedActionLogs] = useState<ActionLogClass[]>(
    actionLogs.asArray.sort((a, b) => a.index - b.index)
  )

  const scrollToBottom = useCallback(
    (element: HTMLDivElement) => {
      if (timeoutId.current !== null) {
        window.clearTimeout(timeoutId.current)
      }
      setHideButton(true)
      timeoutId.current = window.setTimeout(() => {
        setHideButton(false)
      }, Math.abs(element.scrollHeight - element.scrollTop) / 2)
      element.scrollTo({
        top: element.scrollHeight,
        behavior: "smooth",
      })
    },
    [timeoutId, setHideButton]
  )

  useEffect(() => {
    setSortedActionLogs(actionLogs.asArray.sort((a, b) => a.index - b.index))
  }, [actionLogs])

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
  }, [actionLogs.allIds.length, isNearBottom])

  useEffect(() => {
    setNewNotifications(true)
  }, [actionLogs.allIds.length])

  useEffect(() => {
    const scrollableDiv = notificationListRef.current
    if (scrollableDiv === null || !initiateScrollDown) return
    setNewNotifications(false)
    scrollToBottom(scrollableDiv)
    setInitiateScrollDown(false)
  }, [initiateScrollDown, scrollToBottom])

  return (
    <div className="flex-1 flex flex-col overflow-y-auto relative">
      <h3 className="leading-lg m-2 ml-2 text-base text-neutral-600 dark:text-neutral-100">
        Notifications
      </h3>
      <div
        ref={notificationListRef}
        className="h-full overflow-y-auto py-2 bg-white dark:bg-neutral-600 border border-solid border-neutral-200 dark:border-neutral-750 rounded shadow-inner flex flex-col gap-2 scroll-smooth"
      >
        {actionLogs &&
          sortedActionLogs.map((actionLog, index) => {
            const previous = index > 0 ? sortedActionLogs[index - 1] : null
            const previousStep = previous ? steps.byId[previous.step] : null
            const currentStep = steps.byId[actionLog.step]
            const previousPhase = previousStep
              ? phases.byId[previousStep.phase]
              : null
            const currentPhase = phases.byId[currentStep.phase]
            const showPhase = previousPhase?.id !== currentPhase.id
            const previousTurn = previousPhase
              ? turns.byId[previousPhase.turn]
              : null
            const currentTurn = turns.byId[currentPhase.turn]
            const showTurn = previousTurn?.id !== currentTurn.id
            return (
              <div key={index}>
                {showPhase && (
                  <div className="w-full flex items-end pb-2">
                    <div className="grow mb-[11px] h-[2px] bg-tyrian-200 dark:bg-tyrian-500" />

                    <span className="text-sm px-3 py-0.5 rounded bg-tyrian-200 dark:bg-tyrian-500 flex flex-col">
                      {showTurn && (
                        <span className="text-center px-2 text-lg">
                          Turn {currentTurn.index}
                        </span>
                      )}
                      {currentPhase.name} Phase
                    </span>
                    <div className="grow mb-[11px] h-[2px] bg-tyrian-200 dark:bg-tyrian-500" />
                  </div>
                )}

                <div className="px-2">
                  <ActionLog key={actionLog.id} notification={actionLog} />
                </div>
              </div>
            )
          })}
      </div>
      {!isNearBottom && !hideButton && (
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
          <IconButton onClick={() => setInitiateScrollDown(true)} size="large">
            <Badge badgeContent={newNotifications ? "New" : 0} color="primary">
              <ExpandCircleDown fontSize="inherit" />
            </Badge>
          </IconButton>
        </div>
      )}
    </div>
  )
}

export default NotificationList
