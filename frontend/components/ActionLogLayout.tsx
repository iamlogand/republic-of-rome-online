import { CSSProperties, ReactNode, useEffect, useState } from "react"
import { Alert, Tooltip } from "@mui/material"
import Cookies from "js-cookie"
import Faction from "@/classes/Faction"
import { useCookieContext } from "@/contexts/CookieContext"
import formatDate, { formatElapsedDate } from "@/functions/date"
import ActionLog from "@/classes/ActionLog"
import { useGameContext } from "@/contexts/GameContext"

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
  const { turns, phases, steps } = useGameContext()
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

  // Get phase and turn
  const matchingStep = steps.asArray.find((s) => s.id === actionLog.step)
  const matchingPhase = matchingStep
    ? phases.asArray.find((p) => p.id === matchingStep.phase)
    : null
  const matchingTurn = matchingPhase
    ? turns.asArray.find((t) => t.id === matchingPhase.turn)
    : null

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

  const getTooltipTitle = () => {
    if (!timezone) return null
    const dateText = formatDate(actionLog.creation_date, timezone)

    // If it's a new turn, just show the date
    if (actionLog.type === "new_turn") return dateText

    return `Turn ${matchingTurn?.index}, ${matchingPhase?.name} Phase, ${dateText}`
  }

  return (
    <Alert icon={icon} style={getStyle()}>
      {timezone && (
        <div className="absolute right-2 top-0.5 text-xs opacity-90 cursor-default">
          <Tooltip title={getTooltipTitle()} arrow>
            <span>{formatElapsedDate(actionLog.creation_date, timezone)}</span>
          </Tooltip>
        </div>
      )}
      <b>{title}</b>
      <span className="text-pretty">{children}</span>
    </Alert>
  )
}

export default ActionLogLayout
