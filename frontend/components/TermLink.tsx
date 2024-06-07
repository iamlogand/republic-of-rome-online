import { MouseEvent, useState } from "react"
import Image, { StaticImageData } from "next/image"
import { Link, Popover } from "@mui/material"

import HraoIcon from "@/images/icons/hrao.svg"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import PriorConsulIcon from "@/images/icons/priorConsul.svg"
import SenatorIcon from "@/images/icons/senator.svg"
import { useGameContext } from "@/contexts/GameContext"
import SelectedDetail from "@/types/SelectedDetail"

const POPOVER_DELAY = 200

// Map of term names to images
const termImages: { [key: string]: StaticImageData } = {
  HRAO: HraoIcon,
  "Prior Consul": PriorConsulIcon,
  "Rome Consul": RomeConsulIcon,
  Senator: SenatorIcon,
  "Temporary Rome Consul": RomeConsulIcon,
}

interface TermLinkProps {
  name: string
  displayName?: string
  includeIcon?: boolean
  disabled?: boolean
  unstyled?: boolean
  plural?: boolean
  hideText?: boolean
}

// Icon link for a game term
const TermLink = ({
  name,
  displayName,
  includeIcon,
  disabled,
  plural,
  hideText,
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

  const getContent = () => (
    <>
      {includeIcon && (
        <Image
          src={getIcon()}
          height={24}
          width={24}
          alt={`${name} Icon`}
          className="mt-[-5px] align-middle ml-[-2px] mr-0.5"
        />
      )}
      {!hideText && (
        <span>
          {displayName ?? name}
          {plural ? "s" : ""}
        </span>
      )}
    </>
  )

  // Get the JSX for the link
  const getLink = () => {
    if (disabled) return <span>{getContent()}</span>

    return (
      <Link
        href="#"
        onClick={handleClick}
        sx={{ verticalAlign: "baseline" }}
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
            {getContent()}
            {displayName ?? name}
          </div>
        </Popover>
      )}
    </>
  )
}

export default TermLink
