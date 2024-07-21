import { MouseEvent, useState } from "react"
import Image, { StaticImageData } from "next/image"
import { Link, Popover } from "@mui/material"
import chroma from "chroma-js"

import HraoIcon from "@/images/icons/hrao.svg"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import PriorConsulIcon from "@/images/icons/priorConsul.svg"
import SenatorIcon from "@/images/icons/senator.svg"
import TaxFarmerIcon from "@/images/icons/taxFarmer.svg"
import ArmamentsIcon from "@/images/icons/armaments.svg"
import GrainIcon from "@/images/icons/grain.svg"
import { useGameContext } from "@/contexts/GameContext"
import SelectedDetail from "@/types/SelectedDetail"
import TalentsIcon from "@/images/icons/talents.svg"
import { Neutral600 } from "@/themes/colors"

const POPOVER_DELAY = 200

// Map of term names to images
const termImages: { [key: string]: StaticImageData } = {
  HRAO: HraoIcon,
  "Prior Consul": PriorConsulIcon,
  "Rome Consul": RomeConsulIcon,
  Senator: SenatorIcon,
  "Temporary Rome Consul": RomeConsulIcon,
  Armaments: ArmamentsIcon,
  "Ship Building": TaxFarmerIcon,
  Grain: GrainIcon,
  "Harbor Fees": TaxFarmerIcon,
  Mining: TaxFarmerIcon,
  "Land Commissioner": TaxFarmerIcon,
  "Tax Farmer": TaxFarmerIcon,
  "Personal Revenue": TalentsIcon,
  Talent: TalentsIcon,
}

interface TermLinkProps {
  name: string
  displayName?: string
  includeIcon?: boolean
  disabled?: boolean
  hiddenUnderline?: boolean
  plural?: boolean
  hideText?: boolean
  size?: "small" | "medium" | "large"
}

// Icon link for a game term
const TermLink = ({
  name,
  displayName,
  includeIcon,
  disabled,
  hiddenUnderline,
  plural,
  hideText,
  size,
}: TermLinkProps) => {
  const { setSelectedDetail, setDialog } = useGameContext()

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

  // Use the name to get the correct image
  const getIcon = (): StaticImageData | string => {
    if (termImages.hasOwnProperty(name)) return termImages[name]
    else return ""
  }

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement, globalThis.MouseEvent>
  ) => {
    event.preventDefault()
    setDialog(null)
    setSelectedDetail({ type: "Term", name: name } as SelectedDetail)
  }

  const getContent = () => {
    let iconSize = 24
    let tailwindTextSize = "inherit"
    if (!hideText) {
      switch (size) {
        case "small":
          iconSize = 20
          tailwindTextSize = "sm"
          break
        case "medium":
          iconSize = 24
          tailwindTextSize = "base"
          break
        case "large":
          iconSize = 28
          tailwindTextSize = "lg"
          break
      }
    }
    return (
      <>
        {includeIcon && (
          <Image
            src={getIcon()}
            height={iconSize}
            width={iconSize}
            alt={`${name} Icon`}
            className="mt-[-5px] align-middle ml-[-2px] mx-px"
          />
        )}
        {!hideText && (
          <span className={`text-${tailwindTextSize}`}>
            {displayName ?? name}
            {plural ? "s" : ""}
          </span>
        )}
      </>
    )
  }

  // Get the JSX for the link
  const getLink = () => {
    if (disabled) return <span>{getContent()}</span>
    return (
      <Link
        href="#"
        onClick={handleClick}
        sx={{
          verticalAlign: "baseline",
          textDecoration: hiddenUnderline ? "none" : undefined,
          "&:hover": {
            textDecoration: hiddenUnderline
              ? `underline ${chroma(Neutral600).alpha(0.6)}`
              : undefined,
          },
        }}
        color="secondary.dark"
      >
        {getContent()}
      </Link>
    )
  }

  return (
    <>
      <span onMouseEnter={handleOpen} onMouseLeave={handleClose}>
        {getLink()}
      </span>

      {open && hideText && (
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
          <div className="py-2 px-3">
            {getContent()} {displayName ?? name}
            {plural ? "s" : ""}
          </div>
        </Popover>
      )}
    </>
  )
}

export default TermLink
