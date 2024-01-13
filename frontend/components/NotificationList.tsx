import { useGameContext } from "@/contexts/GameContext"
import { ExpandCircleDown } from "@mui/icons-material"
import { IconButton } from "@mui/material"
import { useEffect, useRef, useState } from "react"
import ActionLog from "@/components/actionLogs/ActionLog"

const NotificationList = () => {
  const { notifications } = useGameContext()
  const notificationListRef = useRef<HTMLDivElement>(null)
  const [initiateScrollDown, setInitiateScrollDown] = useState(false)
  const [isNearBottom, setIsNearBottom] = useState(true)

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

  return (
    <div className="flex-1 flex flex-col overflow-y-auto relative">
      <h3 className="leading-lg m-2 ml-2 text-base text-stone-600">
        Notifications
      </h3>
      {!isNearBottom && (
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
          <IconButton onClick={() => setInitiateScrollDown(true)} size="large">
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
              <ActionLog key={notification.id} notification={notification} />
            ))}
      </div>
    </div>
  )
}

export default NotificationList
