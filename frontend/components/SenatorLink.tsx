import { Link } from "@mui/material"

import { useGameContext } from '@/contexts/GameContext'
import Senator from "@/classes/Senator"
import SelectedEntity from "@/types/selectedEntity"

interface SenatorLinkProps {
  senator: Senator
}

const SenatorLink = (props: SenatorLinkProps) => {
  const { setSelectedEntity } = useGameContext()

  const handleClick = () => {
    if (props.senator) setSelectedEntity({className: "Senator", id: props.senator.id} as SelectedEntity)
  }

  return (
    <Link component="button" onClick={handleClick} sx={{ verticalAlign: "baseline", userSelect: 'auto' }}>{props.senator.displayName}</Link>
  )
}

export default SenatorLink