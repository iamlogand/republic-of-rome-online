import { MouseEvent, useState } from "react"
import { SenatorFactListItem } from "@/components/SenatorFactList"
import { Popover } from "@mui/material"
import SenatorFact from "@/components/SenatorFact"

const POPOVER_DELAY = 200

interface HiddenSenatorFactsProps {
  items: SenatorFactListItem[]
}

const HiddenSenatorFacts = ({ items }: HiddenSenatorFactsProps) => {
  // Popover stuff
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null)
  const handleOpen = (event: MouseEvent<HTMLElement>) => {
    const currentTarget = event.currentTarget
    const newTimeoutId = setTimeout(() => {
      setAnchorEl(currentTarget)
    }, POPOVER_DELAY)

    setTimeoutId(newTimeoutId)
  }
  const handleClose = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    setAnchorEl(null)
  }
  const open = Boolean(anchorEl)

  return (
    <>
      <span
        className="inline-block px-0.5 py-1 select-none"
        onMouseEnter={handleOpen}
        onMouseLeave={handleClose}
      >
        <span className="relative top-[-1px] text-sm rounded px-0.5 text-white bg-neutral-550 dark:bg-black">
          +{items.length}
        </span>
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
          <div className="py-2 px-3 flex flex-col gap-0.5">
            {items.map((item, index) => (
              <SenatorFact
                key={index}
                name={item.name}
                termName={item.termName}
              />
            ))}
          </div>
        </Popover>
      )}
    </>
  )
}

export default HiddenSenatorFacts
