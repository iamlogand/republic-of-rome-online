import Image, { StaticImageData } from "next/image"
import { Link } from "@mui/material"

import { Tooltip } from "@mui/material"
import HraoIcon from "@/images/icons/hrao.svg"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import PriorConsulIcon from "@/images/icons/priorConsul.svg"
import SenatorIcon from "@/images/icons/senator.svg"
import { useGameContext } from "@/contexts/GameContext"
import SelectedDetail from "@/types/SelectedDetail"

// Map of term names to images
const termImages: { [key: string]: StaticImageData } = {
  HRAO: HraoIcon,
  "Rome Consul": RomeConsulIcon,
  "Prior Consul": PriorConsulIcon,
  Senator: SenatorIcon,
}

interface TermLinkProps {
  name: string
  displayName?: string
  tooltipTitle?: string
  includeIcon?: boolean
  disabled?: boolean
  unstyled?: boolean
}

// Icon link for a game term
const TermLink = ({
  name,
  displayName,
  tooltipTitle,
  includeIcon,
  disabled,
}: TermLinkProps) => {
  const { selectedDetail, setSelectedDetail, dialog, setDialog } =
    useGameContext()

  // Use the name to get the correct image
  const getIcon = (): StaticImageData | string => {
    if (termImages.hasOwnProperty(name)) return termImages[name]
    else return ""
  }

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement, MouseEvent>
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
      {displayName ?? name}
    </>
  )

  // Get the JSX for the link
  const getLink = () => {
    if (
      disabled ||
      (selectedDetail?.type === "Term" && selectedDetail.name === name)
    )
      return <span>{getContent()}</span>

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

  if (tooltipTitle) {
    return (
      <Tooltip title={tooltipTitle} arrow>
        {getLink()}
      </Tooltip>
    )
  } else {
    return getLink()
  }
}

export default TermLink
