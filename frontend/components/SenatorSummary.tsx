import { MouseEvent, ReactNode, useState } from "react"
import Senator from "@/classes/Senator"
import { Popover } from "@mui/material"
import AttributeFlex, { Attribute } from "@/components/AttributeFlex"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import VotesIcon from "@/images/icons/votes.svg"
import SenatorFactionAndFacts from "@/components/SenatorFactionAndFacts"

interface SenatorSummaryProps {
  senator: Senator
  children: ReactNode
}

const SenatorSummary = ({ senator, children }: SenatorSummaryProps) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null)
  const handleOpen = (event: MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }
  const handleClose = () => {
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
      <Popover
        sx={{
          pointerEvents: "none",
          marginTop: "4px",
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
        onClose={handleClose}
        disableRestoreFocus
      >
        <div className="py-3 px-4 max-w-[260px] flex flex-col gap-4">
          <p className="font-semibold w-full text-center">
            {senator.displayName}
          </p>
          <SenatorFactionAndFacts senator={senator} />
          <div className="flex justify-center">
            <AttributeFlex attributes={attributeItems}></AttributeFlex>
          </div>
        </div>
      </Popover>
    </>
  )
}

export default SenatorSummary
