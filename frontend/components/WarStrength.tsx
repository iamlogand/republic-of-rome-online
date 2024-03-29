import { useState, MouseEvent } from "react"
import EnemyLeader from "@/classes/EnemyLeader"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import { Popover, capitalize } from "@mui/material"
import FormattedWarName from "@/components/FormattedWarName"

interface WarStrengthProps {
  war: War
  type: "land" | "naval"
}

const WarStrength = ({ war, type }: WarStrengthProps) => {
  const { wars, enemyLeaders } = useGameContext()

  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)
  const handlePopoverOpen = (event: MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }
  const handlePopoverClose = () => {
    setAnchorEl(null)
  }
  const open = Boolean(anchorEl)

  const matchingActiveWars = wars.asArray.filter(
    (matchingWar) =>
      matchingWar.name === war.name &&
      matchingWar.id !== war.id &&
      ["active", "unprosecuted"].includes(matchingWar.status)
  )
  const matchingEnemyLeaders = enemyLeaders.asArray.filter(
    (leader: EnemyLeader) => leader.currentWar === war.id
  )

  const baseStrength = type === "land" ? war.landStrength : war.navalStrength
  let modifiedStrength = type === "land" ? war.landStrength : war.navalStrength
  modifiedStrength *= matchingActiveWars.length + 1
  modifiedStrength += matchingEnemyLeaders.reduce(
    (total, leader) => total + leader.strength,
    0
  )

  if (matchingEnemyLeaders.length === 0 && matchingActiveWars.length === 0) {
    return (
      <b className="select-none">
        {baseStrength} {capitalize(type)}
      </b>
    )
  } else {
    return (
      <span className="select-none">
        <b
          className="text-red-500 dark:text-red-400"
          onMouseEnter={handlePopoverOpen}
          onMouseLeave={handlePopoverClose}
          style={{ textDecoration: open ? "underline" : "none" }}
        >
          {modifiedStrength} {capitalize(type)}
        </b>
        <Popover
          sx={{
            pointerEvents: "none",
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
          onClose={handlePopoverClose}
          disableRestoreFocus
        >
          <div className="py-3 px-4 flex flex-col gap-1">
            <p>
              Base {capitalize(type)} Strength{" "}
              <span className="font-bold">{baseStrength}</span>
            </p>
            {matchingActiveWars.length > 0 &&
              matchingActiveWars.map((matchingWar) => (
                <p key={matchingWar.id}>
                  <FormattedWarName war={matchingWar} />{" "}
                  <span className="text-red-500 dark:text-red-400 font-bold">
                    <span className="mr-px">+</span>
                    {baseStrength}
                  </span>
                </p>
              ))}
            {matchingEnemyLeaders.length > 0 &&
              matchingEnemyLeaders.map((leader) => (
                <p key={leader.id}>
                  {leader.name}{" "}
                  <span className="text-red-500 dark:text-red-400 font-bold">
                    <span className="mr-px">+</span>
                    {leader.strength}
                  </span>
                </p>
              ))}
          </div>
        </Popover>
      </span>
    )
  }
}

export default WarStrength
