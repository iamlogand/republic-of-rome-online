import { MouseEvent, ReactNode, useState } from "react"
import Faction from "@/classes/Faction"
import { useGameContext } from "@/contexts/GameContext"
import { Popover } from "@mui/material"
import FactionLink from "./FactionLink"
import FactionIcon from "./FactionIcon"

interface FactionSummaryProps {
  faction: Faction
  children: ReactNode
  inline?: boolean
}

const FactionSummary = ({ faction, children, inline }: FactionSummaryProps) => {
  const { allPlayers } = useGameContext()

  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null)
  const handleOpen = (event: MouseEvent<HTMLElement>) => {
    const currentTarget = event.currentTarget
    const newTimeoutId = setTimeout(() => {
      setAnchorEl(currentTarget)
    }, 200) // Delay before opening the popover

    setTimeoutId(newTimeoutId)
  }
  const handleClose = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    setAnchorEl(null)
  }
  const open = Boolean(anchorEl)

  // Get faction-specific data
  const player = allPlayers.byId[faction.player] ?? null

  return (
    <>
      <span
        onMouseEnter={handleOpen}
        onMouseLeave={handleClose}
        style={{ display: inline ? "inline" : "flex" }}
      >
        {children}
      </span>
      {open && (
        <Popover
          sx={{
            pointerEvents: "none",
            overflowX: "visible",
            overflowY: "visible",
            marginTop: "8px",
          }}
          open={open}
          anchorEl={anchorEl}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "left",
          }}
          transformOrigin={{
            vertical: "top",
            horizontal: "left",
          }}
          onClose={handleClose}
          disableRestoreFocus
        >
          <div className="py-3 px-4 max-w-[260px]">
            <span style={{ marginRight: 4 }}>
              <FactionIcon faction={faction} size={17} />
            </span>
            <span className="font-semibold">{faction.getName()} Faction </span>{" "}
            of {player.user?.username ?? "unknown user"}
          </div>
        </Popover>
      )}
    </>
  )
}

export default FactionSummary
