import { useState, useEffect } from 'react'

import SenatorPortrait from '@/components/SenatorPortrait'
import Player from '@/classes/Player'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import styles from './SenatorListItem.module.css'
import FactionIcon from './FactionIcon'
import { useGameContext } from '@/contexts/GameContext'
import skillsJSON from "@/data/skills.json"
import SenatorLink from '@/components/SenatorLink'

interface SenatorListItemProps {
  senator: Senator
  selectableSenators?: boolean
  selectableFactions?: boolean
  radioSelected?: boolean
}

// Item in the senator list
const SenatorListItem = (props: SenatorListItemProps) => {
  const { allPlayers, allFactions } = useGameContext()
 
  // Faction that this senator is aligned to
  const [faction, setFaction] = useState<Faction | null>(null)
  useEffect(() => {
    setFaction(allFactions.byId[props.senator.faction] ?? null)
  }, [allFactions, props.senator, setFaction])

  // Player that controls this senator
  const [player, setPlayer] = useState<Player | null>(null)
  useEffect(() => {
    if (faction) setPlayer(allPlayers.byId[faction.player] ?? null)
  }, [allPlayers, faction, setFaction])

  return (
    <div key={props.senator.id} className={`${styles.senatorListItem} ${props.radioSelected ? styles.radioSelected : ''}`}>
      <SenatorPortrait senator={props.senator} size={80} selectable={props.selectableSenators} />
      <div className={styles.primaryArea}>
        <p><b><SenatorLink senator={props.senator} /></b></p>
        
        <p>
          {faction && player ?
            <span>
              <span style={{marginLeft: 2, marginRight: 8}}><FactionIcon faction={faction} size={17} selectable={props.selectableFactions} /></span>
              {faction.getName()} Faction ({player.user?.username})
            </span>
            :
            (props.senator.alive ? 'Unaligned' : 'Dead')
          }
        </p>
        <div className={styles.attributeListContainer}>
          <div className={styles.attributeList}>
            <div aria-label="Military" style={{
              backgroundColor: skillsJSON.colors.number["military"],
              boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number["military"]}`
            }}>
              {props.senator.military}
            </div>
            <div aria-label="Oratory" style={{
              backgroundColor: skillsJSON.colors.number["oratory"],
              boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number["oratory"]}`
            }}>
              {props.senator.oratory}
            </div>
            <div aria-label="Loyalty" style={{
              backgroundColor: skillsJSON.colors.number["loyalty"],
              boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number["loyalty"]}`
            }}>
              {props.senator.loyalty}
            </div>
            <div aria-label="Influence">{props.senator.influence}</div>
            <div aria-label="Talents">{props.senator.talents}</div>
            <div aria-label="Popularity">{props.senator.popularity}</div>
            <div aria-label="Knights">{props.senator.knights}</div>
            <div aria-label="Votes">{props.senator.votes}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SenatorListItem
