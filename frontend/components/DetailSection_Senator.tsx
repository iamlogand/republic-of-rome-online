import { RefObject, useEffect, useState } from "react"

import SenatorPortrait from "@/components/SenatorPortrait"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Senator.module.css"
import sectionStyles from "./DetailSection.module.css"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import skill from "@/data/skill.json"
import Skill from "@/components/Skill"

type AttributeRow = {
  name: "Military" | "Oratory" | "Loyalty";
  value: number; // adjust the type as needed
  maxValue?: number;
  description: string;
};

type normalSkillValue = 1 | 2 | 2 | 4 | 5 | 6
type loyaltySkillValue = 0 | 6 | 7 | 8 | 9 | 10

interface SenatorDetailsProps {
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a senator
const SenatorDetails = (props: SenatorDetailsProps) => {
  const { allPlayers, allFactions, allSenators, allOffices, selectedEntity } = useGameContext()
  
  // Selected senator
  const [senator, setSenator] = useState<Senator | null>(null)
  useEffect(() => {
    if (selectedEntity) setSenator(allSenators.asArray.find(f => f.id === selectedEntity.id) ?? null)
  }, [allFactions, selectedEntity, allSenators, setSenator])
  
  // Faction that this senator is aligned to
  const [faction, setFaction] = useState<Faction | null>(null)
  useEffect(() => {
    if (senator) setFaction(allFactions.asArray.find(f => f.id === senator.faction) ?? null)
  }, [allFactions, senator, setFaction])
  
  // Player that controls this senator
  const [player, setPlayer] = useState<Player | null>(null)
  useEffect(() => {
    if (faction) setPlayer(allPlayers.asArray.find(p => p.id === faction.player) ?? null)
  }, [allPlayers, faction, setPlayer])

  // Calculate senator portrait size.
  // Senator portrait size is determined by JavaScript rather than direct CSS,
  // so it necessary to do something like this to make the portrait responsive.
  const getPortraitSize = () => {
    const detailDivWidth = props.detailSectionRef.current?.offsetWidth
    if (detailDivWidth && detailDivWidth < 416) {
      let width = (detailDivWidth - 20) / 2

      // Round down to a multiple of 12 so that we get a nice size value
      // to reduce imperfections on lower resolution displays.
      return Math.floor(width / 12) * 12;
    } else {
      return 200
    }
  }
  
  if (faction && senator && player) {
    const factionNameAndUser = `${faction.getName()} Faction (${player.user?.username})`
    const office = allOffices.asArray.find(o => o.senator === senator.id) ?? null

    const attributeRows: AttributeRow[] = [
      {name: 'Military', value: senator.military, maxValue: 6,
        description: `${skill.default[senator.military as normalSkillValue]} Commander`
      },
      {name: 'Oratory', value: senator.oratory, maxValue: 6,
        description: `${skill.default[senator.oratory as normalSkillValue]} Orator`
      },
      {name: 'Loyalty', value: senator.loyalty,
      description: `${skill.loyalty[senator.loyalty as loyaltySkillValue]}`}
    ]

    return (
      <div className={sectionStyles.detailSectionInner}>
        <div className={styles.primaryArea}>
          <div className={styles.portraitContainer}><SenatorPortrait senator={senator} size={getPortraitSize()} /></div>
          <div className={styles.textContainer}>
            <p><b>{senator!.name}</b></p>
            <p>
              {factionNameAndUser ?
                <span>
                  <span style={{marginRight: 8}}><FactionIcon faction={faction} size={17} clickable /></span>
                  {"Aligned to the"} {factionNameAndUser}
                </span>
                :
                'Unaligned'
              }
            </p>
            {office && <p>Serving as <b>{office?.name}</b></p>}
          </div>
        </div>
        <div className={styles.attributeContainer}>
          <div className={styles.fixedAttributeContainer}>
            {attributeRows.map(row => (
              <div key={row.name} className={styles.attribute}>
                <div className={styles.attributeNameAndValue}>
                  <div>{row.name}</div>
                  <div><i>{row.description}</i></div>
                  <div><Skill name={row.name} value={row.value} /></div>
                </div>
                <progress id="file" value={row.value} max={row.maxValue ?? 10} className={styles.attributeBar}></progress>
              </div>
            ))}
          </div>
          <div className={styles.variableAttributeContainer}>
            <div><div><div>Influence</div><div>{senator.influence}</div></div></div>
            <div><div><div>Talents</div><div>{senator.talents}</div></div></div>
            <div><div><div>Popularity</div><div>{senator.popularity}</div></div></div>
            <div><div><div>Knights</div><div>{senator.knights}</div></div></div>
          </div>
        </div>
      </div>
    )
  } else {
    return null
  }
}

export default SenatorDetails
