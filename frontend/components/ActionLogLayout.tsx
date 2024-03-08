import { CSSProperties, ReactNode, useEffect, useState } from "react"
import { Alert, Tooltip } from "@mui/material"
import Cookies from "js-cookie"
import Faction from "@/classes/Faction"
import { useCookieContext } from "@/contexts/CookieContext"
import formatDate, { formatElapsedDate } from "@/functions/date"
import ActionLog from "@/classes/ActionLog"

interface ActionLogLayoutProps {
  actionLog: ActionLog
  icon: ReactNode
  title: ReactNode
  children: ReactNode
  faction?: Faction
}

const ActionLogLayout = ({
  actionLog,
  icon,
  title,
  children,
  faction,
}: ActionLogLayoutProps) => {
  const { darkMode } = useCookieContext()
  const timezone = Cookies.get("timezone")

  // update the state to force rendering every 5 seconds
  const [_, setRefreshKey] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshKey((oldKey) => oldKey + 1)
    }, 5000)

    return () => {
      clearInterval(interval) // cleanup on unmount
    }
  }, [])

  const getStyle = () => {
    let style: CSSProperties = { position: "relative" }
    if (faction) {
      style.backgroundColor = darkMode
        ? faction.getColor(900)
        : faction.getColor(100)
      style.border = `solid 1px ${
        darkMode ? faction.getColor(950) : faction.getColor(300)
      }`
    }
    return style
  }

  return (
    <Alert icon={icon} style={getStyle()}>
      {timezone && (
        <div className="absolute right-2 top-0.5 text-xs opacity-90 cursor-default">
          <Tooltip title={formatDate(actionLog.creation_date, timezone)} arrow>
            <span>{formatElapsedDate(actionLog.creation_date, timezone)}</span>
          </Tooltip>
        </div>
      )}
      <b>{title}</b>
      {children}
    </Alert>
  )
}

export default ActionLogLayout
