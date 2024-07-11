import { useGameContext } from "@/contexts/GameContext"
import { ExpandCircleDown } from "@mui/icons-material"
import { Badge, IconButton } from "@mui/material"
import { useCallback, useEffect, useRef, useState } from "react"
import ActionLog from "@/components/ActionLog"
import ActionLogClass from "@/classes/ActionLog"
import TermLink from "@/components/TermLink"

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

  const dividerLine = (
    <div className="grow h-[2px] bg-tyrian-200 dark:bg-tyrian-500" />
  )

  const renderDivider = (phaseName: string, turnIndex: number | null) => {
    return (
      <div className="w-full flex items-center">
        {dividerLine}
        <span className="text-sm px-3 py-0.5 rounded bg-tyrian-200 dark:bg-tyrian-500 flex flex-col">
          {turnIndex !== null && (
            <span className="text-center px-2 text-lg">
              <TermLink name="Turn" /> {turnIndex}
            </span>
          )}
          <TermLink name={`${phaseName} Phase`} />
        </span>
        {dividerLine}
      </div>
    )
  }

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
            const previousLog = index > 0 ? sortedActionLogs[index - 1] : null
            const previousLogStep = previousLog
              ? steps.byId[previousLog.step]
              : null
            const currentLogStep = steps.byId[actionLog.step]
            const previousLogPhase = previousLogStep
              ? phases.byId[previousLogStep.phase]
              : null
            const currentLogPhase = phases.byId[currentLogStep.phase]
            const showPhase = previousLogPhase?.id !== currentLogPhase.id
            const previousLogTurn = previousLogPhase
              ? turns.byId[previousLogPhase.turn]
              : null
            const currentLogTurn = turns.byId[currentLogPhase.turn]
            const showTurn = previousLogTurn?.id !== currentLogTurn.id
            return (
              <div key={index} className="flex flex-col gap-2">
                {showPhase &&
                  renderDivider(
                    currentLogPhase.name,
                    showTurn ? currentLogTurn.index : null
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
