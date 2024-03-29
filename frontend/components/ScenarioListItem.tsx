import { Tooltip } from "@mui/material"
import { ReactNode } from "react"

interface ScenarioListItemProps {
  children: ReactNode
  scenario: "E" | "M" | "L"
}

const ScenarioListItem = ({ children, scenario }: ScenarioListItemProps) => {
  if (scenario === "E") {
    return (
      <li className="text-red-600 dark:text-red-300">
        {children}{" "}
        <Tooltip title="Early Republic Scenario" arrow>
          <span className="text-xs cursor-default">E</span>
        </Tooltip>
      </li>
    )
  } else if (scenario === "M") {
    return (
      <li className="text-green-600 dark:text-green-300">
        {children}{" "}
        <Tooltip title="Middle Republic Scenario" arrow>
          <span className="text-xs cursor-default">M</span>
        </Tooltip>
      </li>
    )
  } else {
    return (
      <li className="text-blue-600 dark:text-blue-300">
        {children}{" "}
        <Tooltip title="Late Republic Scenario" arrow>
          <span className="text-xs cursor-default">L</span>
        </Tooltip>
      </li>
    )
  }
}

export default ScenarioListItem
