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
    if (props.faction?.id) setSelectedEntity({className: "Faction", id: props.faction.id} as SelectedEntity)
  }
  
  if (props.faction && props.faction) {

    const svg = (
      <svg
        className={styles.factionIcon}
        height={props.size}
        viewBox="0 0 0.9 1"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M0,0 H0.9 V1 L0.45,0.75 L0,1 Z" fill={props.faction.getColor("primary")} stroke="#000" strokeWidth="2" vectorEffect="non-scaling-stroke" />
      </svg>
    )

    const svgInsideButton = (
      <button onClick={handleClick} className={styles.button} style={{height: props.size, lineHeight: `${props.size}px`}}>
        {svg}
      </button>
    )

    return props.selectable ? svgInsideButton : svg
  } else {
    return null
  }
}

export default FactionIcon
