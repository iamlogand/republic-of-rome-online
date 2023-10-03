import Image, { StaticImageData } from 'next/image'
import { Link } from "@mui/material"

import { Tooltip } from '@mui/material'
import HraoIcon from '@/images/icons/hrao.svg'
import RomeConsulIcon from '@/images/icons/romeConsul.svg'
import styles from './TermLink.module.css'
import { useGameContext } from '@/contexts/GameContext'
import SelectedDetail from '@/types/selectedDetail'

// Map of term names to images
const termImages: { [key: string]: StaticImageData } = {
  "HRAO": HraoIcon,
  "Rome Consul": RomeConsulIcon
}

interface TermLinkProps {
  name: string,
  displayName?: string,
  tooltipTitle?: string,
  includeIcon?: boolean
}

// Icon link for a game term
const TermLink = ({ name, displayName, tooltipTitle, includeIcon }: TermLinkProps) => {
  const { setSelectedDetail } = useGameContext()

  // Use the name to get the correct image
  const getIcon = (): StaticImageData | string => {
    if (termImages.hasOwnProperty(name)) return termImages[name]
    else return ""
  }

  const handleClick = () => {
    setSelectedDetail({type: "Term", name: name} as SelectedDetail)
  }

  // Get the JSX for the link
  const getLink = () => (
    <Link onClick={handleClick} sx={{ verticalAlign: "baseline", userSelect: 'auto', cursor: 'pointer' }}>
      {includeIcon && <Image src={getIcon()} height={28} width={28} alt={`${name} Icon`} className={styles.icon} />}
      {displayName ?? name}
    </Link>
  )

  if (tooltipTitle) {
    return <Tooltip title={tooltipTitle} enterDelay={500} arrow>{getLink()}</Tooltip>
  } else {
    return getLink()
  }
}

export default TermLink
