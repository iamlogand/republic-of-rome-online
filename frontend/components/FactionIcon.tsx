import { useState } from "react"

import styles from "./FactionIcon.module.css"
import Faction from '@/classes/Faction'
import SelectedEntity from "@/types/selectedEntity"

interface FactionIconProps {
  faction: Faction | null
  size: number
  setSelectedEntity?: Function
  style?: React.CSSProperties
}

// Small flag icon representing a faction, identifiable by color
const FactionIcon = (props: FactionIconProps) => {
  const [hover, setHover] = useState<boolean>(false)

  const color = props.faction?.getColor()

  const getFillColor = () => {
    if (props.faction) {
      if (hover) {
        return props.faction.getColor("bgHover")  // Background is brighter on mouse hover
      } else {
        return props.faction.getColor("primary")
      }
    }
  }

  const handleClick = () => {
    if (props.setSelectedEntity && props.faction?.id) props.setSelectedEntity({className: "Faction", id: props.faction.id} as SelectedEntity)
  }

  const handleMouseOver = () => {
    if (props.setSelectedEntity) setHover(true)
  }

  const handleMouseLeave = () => {
    setHover(false)
  }
  
  return (
    <svg
      onClick={handleClick}
      onMouseOver={handleMouseOver}
      onMouseLeave={handleMouseLeave}
      className={styles.FactionIcon}
      height={props.size}
      style={props.style}
      viewBox="0 0 1 1.1"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M0,0 H1 V1.1 L0.5,0.8 L0,1.1 Z" fill={getFillColor()} stroke="#000" strokeWidth="2" vectorEffect="non-scaling-stroke" />
    </svg>
  )
}

export default FactionIcon
