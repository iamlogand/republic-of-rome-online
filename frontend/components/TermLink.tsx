import Image, { StaticImageData } from "next/image"
import { Link } from "@mui/material"

import { Tooltip } from "@mui/material"
import HraoIcon from "@/images/icons/hrao.svg"
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import styles from "./TermLink.module.css"
import { useGameContext } from "@/contexts/GameContext"
import SelectedDetail from "@/types/selectedDetail"

// Map of term names to images
const termImages: { [key: string]: StaticImageData } = {
  HRAO: HraoIcon,
  "Rome Consul": RomeConsulIcon,
}

interface TermLinkProps {
  name: string
  displayName?: string
  tooltipTitle?: string
  includeIcon?: boolean
}

// Icon link for a game term
const TermLink = ({
  name,
  displayName,
  tooltipTitle,
  includeIcon,
}: TermLinkProps) => {
  const { selectedDetail, setSelectedDetail } = useGameContext()

  // Use the name to get the correct image
  const getIcon = (): StaticImageData | string => {
    if (termImages.hasOwnProperty(name)) return termImages[name]
    else return ""
  }

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement, MouseEvent>
  ) => {
    event.preventDefault()
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
          className={styles.icon}
        />
      )}
      {displayName ?? name}
    </>
  )

  // Get the JSX for the link
  const getLink = () => {
    if (selectedDetail?.type === "Term" && selectedDetail.name === name)
      return <span>{getContent()}</span>

    return (
      <Link href="#" onClick={handleClick} sx={{ verticalAlign: "baseline" }}>
        {getContent()}
      </Link>
    )
  }

  if (tooltipTitle) {
    return (
      <Tooltip title={tooltipTitle} enterDelay={500} arrow>
        {getLink()}
      </Tooltip>
    )
  } else {
    return getLink()
  }
}

export default TermLink
