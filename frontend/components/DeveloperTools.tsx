import { Checkbox, FormControlLabel, IconButton, Popover } from "@mui/material"
import DeveloperModeIcon from "@mui/icons-material/DeveloperMode"
import React from "react"
import { useGameContext } from "@/contexts/GameContext"
import FactionLink from "@/components/FactionLink"

// A button that opens a popover with debugging tools
const DeveloperTools = () => {
  const {
    game,
    latestTurn,
    latestPhase,
    latestStep,
    allFactions,
    debugShowEntityIds,
    setDebugShowEntityIds,
  } = useGameContext()

  const [anchorElement, setAnchorElement] =
    React.useState<HTMLButtonElement | null>(null)
  const filtersOpen = Boolean(anchorElement)

  // Handle opening the debugging tools popover
  const handleOpenDebuggingToolsClick = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => setAnchorElement(event.currentTarget)

  // Handle closing the debugging tools popover
  const handleCloseFilters = () => setAnchorElement(null)

  // Handle toggling the show entity IDs checkbox
  const handleToggleShowEntityIds = () =>
    debugShowEntityIds
      ? setDebugShowEntityIds(false)
      : setDebugShowEntityIds(true)

  return (
    <>
      <IconButton
        aria-label="debugging tools"
        onClick={handleOpenDebuggingToolsClick}
      >
        <DeveloperModeIcon />
      </IconButton>
      <Popover
        open={filtersOpen}
        anchorEl={anchorElement}
        onClose={handleCloseFilters}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "center",
        }}
      >
        <div className="py-2 flex flex-col">
          <h4 className="px-4 mb-1 text-neutral-500 text-sm">Developer Tools</h4>
          <div className="w-full h-px bg-neutral-200 dark:bg-neutral-800 my-1"></div>
          <div className="px-4">
            <table>
              <tr>
                <th className="text-left">Entity</th>
                <th className="pl-2 text-left">ID</th>
              </tr>
              <tr>
                <td>Game ID</td>
                <td className="pl-2">{game?.id}</td>
              </tr>
              <tr>
                <td>Turn ID</td>
                <td className="pl-2">{latestTurn?.id}</td>
              </tr>
              <tr>
                <td>Phase ID</td>
                <td className="pl-2">{latestPhase?.id}</td>
              </tr>
              <tr>
                <td>Step ID</td>
                <td className="pl-2">{latestStep?.id}</td>
              </tr>
              {allFactions.asArray.map((faction, index) => (
                <tr key={index}>
                  <td>
                    <FactionLink faction={faction} includeIcon />
                  </td>
                  <td className="pl-2">{faction.id}</td>
                </tr>
              ))}
            </table>
          </div>
          <div className="w-full h-px bg-neutral-200 dark:bg-neutral-800 my-1"></div>
          <FormControlLabel
            control={<Checkbox checked={debugShowEntityIds} />}
            label="Show Entity IDs"
            onChange={handleToggleShowEntityIds}
            className="px-4"
          />
        </div>
      </Popover>
    </>
  )
}

export default DeveloperTools
