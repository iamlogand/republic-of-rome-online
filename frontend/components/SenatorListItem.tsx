import { Tooltip } from '@mui/material'

import SenatorPortrait from '@/components/SenatorPortrait'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import styles from './SenatorListItem.module.css'
import { useGameContext } from '@/contexts/GameContext'
import skillsJSON from "@/data/skills.json"
import SenatorLink from '@/components/SenatorLink'
import FactionLink from '@/components/FactionLink'

type FixedAttribute = "military" | "oratory" | "loyalty"

type Attribute = {
  name: FixedAttribute | string
  value: number
  fixed?: boolean
}

interface SenatorListItemProps {
  senator: Senator
  selectableSenators?: boolean
  selectableFactions?: boolean
  radioSelected?: boolean
}

// Item in the senator list
const SenatorListItem = ({ senator, ...props }: SenatorListItemProps) => {
  const { allPlayers, allFactions, allTitles } = useGameContext()

  // Get senator-specific data
  const faction: Faction | null = senator.faction ? allFactions.byId[senator.faction] ?? null : null
  const player: Player | null = faction?.player ? allPlayers.byId[faction.player] ?? null : null
  const factionLeader: boolean = allTitles.asArray.some(o => o.senator === senator.id && o.name == 'Faction Leader')

  // Attribute data
  const attributes: Attribute[] = [
    { name: "military", value: senator.military, fixed: true },
    { name: "oratory", value: senator.oratory, fixed: true },
    { name: "loyalty", value: senator.loyalty, fixed: true },
    { name: "influence", value: senator.influence },
    { name: "talents", value: senator.talents },
    { name: "popularity", value: senator.popularity },
    { name: "knights", value: senator.knights },
    { name: "votes", value: senator.votes }
  ]

  // Get JSX for an attribute item
  const getAttributeItem = (item: Attribute) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <Tooltip title={titleCaseName} enterDelay={500} arrow>
        <div aria-label={titleCaseName} style={item.fixed ? {
          backgroundColor: skillsJSON.colors.number[item.name as FixedAttribute],
          boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number[item.name as FixedAttribute]}`
        } : {} }>
          {item.value}
        </div>
      </Tooltip>
    )
  }

  return (
    <div key={senator.id} className={`${styles.senatorListItem} ${props.radioSelected ? styles.radioSelected : ''}`}>
      <SenatorPortrait senator={senator} size={80} selectable={props.selectableSenators} />
      <div className={styles.primaryArea}>
        <p><b><SenatorLink senator={senator} /></b></p>
        <p>
          {faction ?
            (props.selectableFactions &&
              <span>
                <FactionLink faction={faction} includeIcon />
                {factionLeader ? ' Leader' : null}
                {player ? <span> ({player.user?.username})</span> : null}
              </span>
            )
            :
            (senator.alive ? 'Unaligned' : 'Dead')
          }
        </p>
        <div className={styles.attributeListContainer}>
          <div className={styles.attributeList}>
            {attributes.map((item) => getAttributeItem(item))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default SenatorListItem
