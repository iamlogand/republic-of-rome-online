import { useGameContext } from "@/contexts/GameContext"
import { ExpandCircleDown } from "@mui/icons-material"
import { Badge, IconButton } from "@mui/material"
import { useEffect, useRef, useState } from "react"
import ActionLog from "@/components/ActionLog"

const NotificationList = () => {
  const { notifications } = useGameContext()
  const notificationListRef = useRef<HTMLDivElement>(null)
  const [initiateScrollDown, setInitiateScrollDown] = useState(false)
  const [isNearBottom, setIsNearBottom] = useState(true)
  const [newNotifications, setNewNotifications] = useState(false)

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

  const [hideButton, setHideButton] = useState(false)
  const timeoutId = useRef<number | null>(null)

  useEffect(() => {
    if (isNearBottom) setInitiateScrollDown(true)
  }, [notifications.allIds.length, isNearBottom])

  useEffect(() => {
    setNewNotifications(true)
  }, [notifications.allIds.length])

  const scrollToBottom = (element: HTMLDivElement) => {
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
  }

  useEffect(() => {
    const scrollableDiv = notificationListRef.current
    if (scrollableDiv === null || !initiateScrollDown) return
    setNewNotifications(false)
    scrollToBottom(scrollableDiv)
    setInitiateScrollDown(false)
  }, [initiateScrollDown])

  return (
    <div className="flex-1 flex flex-col overflow-y-auto relative">
      <h3 className="leading-lg m-2 ml-2 text-base text-neutral-600 dark:text-neutral-100">
        Notifications
      </h3>
      <div
        ref={notificationListRef}
        className="h-full overflow-y-auto p-2 bg-white dark:bg-neutral-600 border border-solid border-neutral-200 dark:border-neutral-750 rounded shadow-inner flex flex-col gap-2 scroll-smooth"
      >
        {notifications &&
          notifications.asArray
            .sort((a, b) => a.index - b.index)
            .map((notification) => (
              <ActionLog key={notification.id} notification={notification} />
            ))}
      </div>
      {!isNearBottom && !hideButton && (
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
          <IconButton onClick={() => setInitiateScrollDown(true)} size="large">
            <Badge badgeContent={newNotifications ? "New" : 0} color="primary" >
              <ExpandCircleDown fontSize="inherit" />
            </Badge>
          </IconButton>
        </div>
      )}
    </div>
  )
}

export default NotificationList
