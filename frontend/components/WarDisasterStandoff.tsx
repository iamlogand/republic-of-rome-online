import React from "react"
import EnemyLeader from "@/classes/EnemyLeader"
import War from "@/classes/War"
import { useGameContext } from "@/contexts/GameContext"
import { Popover } from "@mui/material"
import getDiceRollProbability from "@/functions/probability"
import { capitalize, get } from "lodash"

interface WarDisasterStandoffProps {
  war: War
  type: "disaster" | "standoff"
}

const WarDisasterStandoff = ({ war, type }: WarDisasterStandoffProps) => {
  const { wars, enemyLeaders } = useGameContext()

  const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null)
  const handlePopoverOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }
  const handlePopoverClose = () => {
    setAnchorEl(null)
  }
  const open = Boolean(anchorEl)

  const matchingEnemyLeaders = enemyLeaders.asArray.filter(
    (leader: EnemyLeader) => leader.currentWar === war.id
  )

  const baseNumbers =
    type === "disaster" ? war.disasterNumbers : war.standoffNumbers
  const baseProbability = getDiceRollProbability(3, baseNumbers)
  const additionalNumbers = matchingEnemyLeaders.map(
    (leader) => (type === "disaster" ? leader.disasterNumber : leader.standoffNumber)
  )
  const modifiedProbability = getDiceRollProbability(3, [...baseNumbers, ...additionalNumbers])

  if (matchingEnemyLeaders.length === 0) {
    return (
      <div>
        <b>{baseProbability}</b> chance of {capitalize(type)}
      </div>
    )
  } else {
    return (
      <span className="select-none">
        <span
          className="text-red-600 dark:text-red-400"
          onMouseEnter={handlePopoverOpen}
          onMouseLeave={handlePopoverClose}
          style={{ textDecoration: open ? "underline" : "none" }}
        >
          <b className="text-red-500 dark:text-red-400">{modifiedProbability}</b> chance of {capitalize(type)}
        </span>
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
          <div className="py-3 px-4 flex flex-col gap-1">
            <p>
              Base {capitalize(type)} chance{" "}
              <span className="font-bold">
                {baseProbability}
              </span>
            </p>
            {matchingEnemyLeaders.length > 0 &&
              matchingEnemyLeaders.map((leader) => {
                const leaderNumber = type === "disaster" ? leader.disasterNumber : leader.standoffNumber
                const leaderProbability = getDiceRollProbability(3, [leaderNumber])
                return (
                  <p key={leader.id}>
                    {leader.name}{" "}
                    <span className="text-red-500 dark:text-red-400 font-bold">
                      <span className="mr-px">+</span>
                      {leaderProbability}
                    </span>
                  </p>
                )
              })}
          </div>
        </Popover>
      </span>
    )
  }
}

export default WarDisasterStandoff
