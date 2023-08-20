import styles from "./FactionIcon.module.css"
import Faction from '@/classes/Faction'

interface FactionIconProps {
  faction: Faction | null
  size: number
  style?: React.CSSProperties
}

const FactionIcon = (props: FactionIconProps) => {

  const color = props.faction?.getColor()
  
  return (
    <svg className={styles.FactionIcon} height={props.size} style={props.style} viewBox="100.96 142.97 .34011 .36099" xmlns="http://www.w3.org/2000/svg">
      <g transform="translate(-.0096116 -.013482)">
        <path d="m100.99 143h0.30429v0.31458l-0.15215-0.0733-0.15214 0.0733z" fill={color} stroke="#000" stroke-width=".035817"/>
      </g>
    </svg>
  )
}

export default FactionIcon
