import { CSSProperties, ReactNode } from "react"
import { Alert } from "@mui/material"
import Cookies from "js-cookie"
import Faction from "@/classes/Faction"
import { useCookieContext } from "@/contexts/CookieContext"
import formatDate from "@/functions/date"
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
        <div className="absolute right-1 top-0.5 text-xs opacity-50">
          {formatDate(actionLog.creation_date, timezone)}
        </div>
      )}
      <b>{title}</b>
      {children}
    </Alert>
  )
}

export default ActionLogLayout
