import { useState } from "react"

import styles from "./FactionIcon.module.css"
import Faction from '@/classes/Faction'
import SelectedEntity from "@/types/selectedEntity"
import { useGameContext } from "@/contexts/GameContext"

interface FactionIconProps {
  faction: Faction | null
  size: number
  selectable?: boolean
}

// Small flag icon representing a faction, identifiable by color
const FactionIcon = (props: FactionIconProps) => {
  const { setSelectedEntity } = useGameContext()

  const handleClick = () => {
    if (props.selectable && props.faction?.id) setSelectedEntity({className: "Faction", id: props.faction.id} as SelectedEntity)
  }
  
  if (props.faction && props.faction) {
    return (
      <svg
        onClick={handleClick}
        className={`${styles.factionIcon} ${props.selectable ? styles.selectable : ""}`}
        height={props.size}
        viewBox="0 0 1 1.1"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M0,0 H1 V1.1 L0.5,0.8 L0,1.1 Z" fill={props.faction.getColor("primary")} stroke="#000" strokeWidth="2" vectorEffect="non-scaling-stroke" />
      </svg>
    )
  } else {
    return null
  }
}

export default FactionIcon
