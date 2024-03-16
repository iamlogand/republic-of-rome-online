import { MouseEvent, ReactNode, useState } from "react"
import Senator from "@/classes/Senator"
import { Popover } from "@mui/material"
import AttributeFlex, { Attribute } from "@/components/AttributeFlex"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import VotesIcon from "@/images/icons/votes.svg"
import SenatorFactionInfo from "@/components/SenatorFactionInfo"
import SenatorPortrait from "@/components/SenatorPortrait"
import SenatorFactList from "@/components/SenatorFactList"

interface SenatorSummaryProps {
  senator: Senator
  children: ReactNode
  portrait?: boolean
  marginTop?: number
}

const SenatorSummary = ({
  senator,
  children,
  portrait,
  marginTop,
}: SenatorSummaryProps) => {
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

  // Attribute data
  const attributeItems: Attribute[] = [
    {
      name: "influence",
      value: senator.influence,
      icon: InfluenceIcon,
    },
    { name: "talents", value: senator.talents, icon: TalentsIcon },
    { name: "votes", value: senator.votes, icon: VotesIcon },
  ]

  return (
    <>
      <div
        onMouseEnter={handleOpen}
        onMouseLeave={handleClose}
        className="inline"
      >
        {children}
      </div>
      {open && (
        <Popover
          sx={{
            pointerEvents: "none",
            marginTop: `${marginTop}px`,
            overflowX: "visible",
            overflowY: "visible",
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
          <div className="py-3 px-4 max-w-[260px] flex flex-col gap-3">
            <div className="flex gap-3">
              {portrait && <SenatorPortrait senator={senator} size={70} />}
              <div
                className="flex flex-col"
                style={portrait ? { gap: 6 } : { gap: 8 }}
              >
                <p className="font-semibold ">{senator.displayName}</p>
                <SenatorFactionInfo senator={senator} />
              </div>
            </div>
            <SenatorFactList senator={senator} />
            <AttributeFlex attributes={attributeItems} />
          </div>
        </Popover>
      )}
    </>
  )
}

export default SenatorSummary
