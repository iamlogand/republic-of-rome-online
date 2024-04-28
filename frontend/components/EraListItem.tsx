import { Tooltip } from "@mui/material"
import { ReactNode } from "react"

interface EraListItemProps {
  children: ReactNode
  era: "E" | "M" | "L"
}

const EraListItem = ({ children, era }: EraListItemProps) => {
  if (era === "E") {
    return (
      <li className="text-red-600 dark:text-red-300">
        {children}{" "}
        <Tooltip title="Early Republic Era" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
      </li>
    )
  } else if (era === "M") {
    return (
      <li className="text-green-600 dark:text-green-300">
        {children}{" "}
        <Tooltip title="Middle Republic Era" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
      </li>
    )
  } else {
    return (
      <li className="text-blue-600 dark:text-blue-300">
        {children}{" "}
        <Tooltip title="Late Republic Era" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
      </li>
    )
  }
}

export default EraListItem
