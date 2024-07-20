import { useRef, useState } from "react"
import { Popover } from "@mui/material"
import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import SenatorPortrait from "@/components/SenatorPortrait"
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown"
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp"
import { useCookieContext } from "@/contexts/CookieContext"
import { Tyrian200, Tyrian500 } from "@/themes/colors"
import SenatorSelectorItem from "@/components//SenatorSelectorItem"

interface SenatorSelectorProps {
  senators: Collection<Senator>
  selectedSenator: Senator | null
  setSelectedSenator: (senator: Senator | null) => void
}

const SenatorSelector = ({
  senators,
  selectedSenator,
  setSelectedSenator,
}: SenatorSelectorProps) => {
  const { darkMode } = useCookieContext()
  const [open, setOpen] = useState(false)
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const sortedSenators = senators.asArray.sort((a, b) =>
    a.displayName.localeCompare(b.displayName)
  )

  const handlePopoverOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget)
    setOpen(true)
  }

  const handlePopoverClose = () => {
    setAnchorEl(null)
    setOpen(false)
  }

  const handleSenatorSelect = (senator: Senator | null) => {
    setSelectedSenator(senator)
    handlePopoverClose()
  }

  return (
    <div ref={containerRef} className="w-full">
      <button
        onClick={handlePopoverOpen}
        className={
          "cursor-pointer bg-transparent text-left p-1 border border-solid rounded w-full h-[70px] flex items-center justify-between \
          border-neutral-300 dark:border-neutral-500 hover:border-neutral-600 dark:hover:border-neutral-200 \
          focus:border-tyrian-500 dark:focus:border-tyrian-200 focus:border-2 focus:p-[3px]"
        }
        style={
          open
            ? {
                borderColor: darkMode ? Tyrian200 : Tyrian500,
                borderWidth: 2,
                padding: 3,
              }
            : {}
        }
      >
        {selectedSenator ? (
          <div className="flex items-center gap-4">
            <SenatorPortrait senator={selectedSenator} size={60} summary />
            <span className="font-semibold">{selectedSenator.displayName}</span>
          </div>
        ) : (
          <div className="ml-4">None</div>
        )}
        {open ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
      </button>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handlePopoverClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left",
        }}
        slotProps={{
          paper: {
            style: {
              width: containerRef.current
                ? containerRef.current.clientWidth
                : undefined,
            },
          },
        }}
      >
        <div className="flex flex-col min-w-[200px] py-2">
          {[null, ...sortedSenators].map((senator) => {
            const isSelected =
              (!selectedSenator && !senator) ||
              (!!selectedSenator && !!senator && selectedSenator.id === senator.id)
            
            return (
              <SenatorSelectorItem
                senator={senator}
                onSelect={handleSenatorSelect}
                selected={isSelected}
              />
            )
          })}
        </div>
      </Popover>
    </div>
  )
}

export default SenatorSelector
