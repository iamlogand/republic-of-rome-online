import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import { Popover } from "@mui/material"
import React from "react"

interface WarStrengthProps {
  war: War
  type: "Land" | "Naval"
}

const WarStrength = ({ war, type }: WarStrengthProps) => {
  const { wars } = useGameContext()

  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null)
  const handlePopoverOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }
  const handlePopoverClose = () => {
    setAnchorEl(null)
  }
  const open = Boolean(anchorEl)

  const baseStrength = type === "Land" ? war.landStrength : war.navalStrength
  const actualStrength =
    type === "Land" ? war.getActualLandStrength() : war.getActualNavalStrength()

  if (baseStrength === actualStrength) {
    return (
      <b>
        {baseStrength} {type}
      </b>
    )
  } else {
    const matchingWarIds = war.matchingWars
    const matchingWars = wars.asArray.filter((w) =>
      matchingWarIds.includes(w.id)
    )

    return (
      <span>
        <b
          className="text-red-500 dark:text-red-400"
          onMouseEnter={handlePopoverOpen}
          onMouseLeave={handlePopoverClose}
          style={{textDecoration: open ? "underline" : "none"}}
        >
          {actualStrength} {type}
        </b>
        <Popover
          sx={{
            pointerEvents: "none",
          }}
          open={open}
          anchorEl={anchorEl}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "center",
          }}
          transformOrigin={{
            vertical: "top",
            horizontal: "center",
          }}
          onClose={handlePopoverClose}
          disableRestoreFocus
        >
          <div className="py-2 px-4 flex flex-col gap-1 dark:bg-stone-700">
            <p>
              Base {type} Strength of {baseStrength}
            </p>
            <div className="text-red-500 dark:text-red-400">
              <p>
                Multiplied by {matchingWarIds.length + 1} due to{" "}
                {matchingWarIds.length > 1
                  ? "Matching Active Wars:"
                  : "a Matching Active War:"}
              </p>
              <ul>
                {matchingWars.map((matchingWar) => (
                  <li key={matchingWar.id}>{matchingWar.getName()}</li>
                ))}
              </ul>
            </div>
          </div>
        </Popover>
      </span>
    )
  }
}

export default WarStrength
