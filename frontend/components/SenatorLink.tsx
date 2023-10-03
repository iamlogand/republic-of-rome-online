import { Link } from "@mui/material"

import { useGameContext } from '@/contexts/GameContext'
import Senator from "@/classes/Senator"
import SelectedDetail from "@/types/selectedDetail"

interface SenatorLinkProps {
  senator: Senator
}

const SenatorLink = (props: SenatorLinkProps) => {
  const { setSelectedDetail } = useGameContext()

  const handleClick = () => {
    if (props.senator) setSelectedDetail({type: "Senator", id: props.senator.id} as SelectedDetail)
  }

  return (
    <Link onClick={handleClick} sx={{ verticalAlign: "baseline", userSelect: 'auto', cursor: 'pointer' }}>{props.senator.displayName}</Link>
  )
}

export default SenatorLink