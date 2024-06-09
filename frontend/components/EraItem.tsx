import { Tooltip } from "@mui/material"
import React from "react"
import { ReactNode } from "react"

interface EraItemProps {
  era: "E" | "M" | "L"
  name: ReactNode
  childList?: ReactNode
  enemyLeader?: boolean
  listItem?: boolean
}

const EraItem = ({
  era,
  name,
  childList,
  enemyLeader,
  listItem,
}: EraItemProps) => {
  const getEra = () => {
    if (era === "E") {
      return (
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
      )
    } else if (era === "M") {
      return (
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
      )
    } else {
      return (
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
      )
    }
  }

  const getClassName = () => {
    if (era === "E") {
      return "text-red-600 dark:text-red-300"
    } else if (era === "M") {
      return "text-green-600 dark:text-green-300"
    } else {
      return "text-blue-600 dark:text-blue-300"
    }
  }

  const getContent = () =>
    React.createElement(
      listItem ? "li" : "span",
      { className: getClassName() },
      React.createElement(
        enemyLeader ? "i" : "span",
        {},
        <>
          {name} {enemyLeader && <span>(Enemy Leader)</span>} {getEra()}
          {childList && <ul>{childList}</ul>}
        </>
      )
    )

  if (listItem) {
    return <li className="text-blue-600 dark:text-blue-300">{getContent()}</li>
  } else {
    return getContent()
  }
}

export default EraItem
