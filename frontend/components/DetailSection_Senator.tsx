import Image from 'next/image'
import { RefObject, useEffect, useState } from "react"

import SenatorPortrait from "@/components/SenatorPortrait"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Senator.module.css"
import sectionStyles from "./DetailSection.module.css"
import FactionIcon from "@/components/FactionIcon"
import { useGameContext } from "@/contexts/GameContext"
import skillsJSON from "@/data/skills.json"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import PopularityIcon from "@/images/icons/popularity.svg"
import KnightsIcon from "@/images/icons/knights.svg"

type FixedAttributeRow = {
  name: "military" | "oratory" | "loyalty"
  value: number
  maxValue?: number
  image: string
  description: string
};

type normalSkillValue = 1 | 2 | 2 | 4 | 5 | 6
type loyaltySkillValue = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10

interface SenatorDetailsProps {
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a senator
const SenatorDetails = (props: SenatorDetailsProps) => {
  const { allPlayers, allFactions, allSenators, allTitles, selectedEntity } = useGameContext()
  
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
  
  // Set data for fixed attributes (military, oratory and loyalty)
  if (faction && senator && player) {
    const factionNameAndUser = `${faction.getName()} Faction (${player.user?.username})`
    const title = allTitles.asArray.find(o => o.senator === senator.id) ?? null

    const attributeRows: FixedAttributeRow[] = [
      {name: 'military', value: senator.military, maxValue: 6, image: MilitaryIcon,
        description: `${skillsJSON.descriptions.default[senator.military as normalSkillValue]} Commander`
      },
      {name: 'oratory', value: senator.oratory, maxValue: 6, image: OratoryIcon,
        description: `${skillsJSON.descriptions.default[senator.oratory as normalSkillValue]} Orator`
      },
      {name: 'loyalty', value: senator.loyalty, image: LoyaltyIcon,
      description: `${skillsJSON.descriptions.loyalty[senator.loyalty as loyaltySkillValue]}`}
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
                  <span style={{marginRight: 8}}><FactionIcon faction={faction} size={17} selectable /></span>
                  {"Aligned to the"} {factionNameAndUser}
                </span>
                :
                'Unaligned'
              }
            </p>
            {title && <p>Serving as <b>{title?.name}</b></p>}
          </div>
        </div>
        <div className={styles.attributeContainer}>
          <div className={styles.fixedAttributeContainer}>
            {attributeRows.map(row => {
              const titleCaseName = row.name[0].toUpperCase() + row.name.slice(1)
              return (
                <div key={row.name} className={styles.attribute}>
                  <div className={styles.attributeNameAndValue}>
                    <div>{titleCaseName}</div>
                    <Image src={row.image} height={34} width={34} alt={`${titleCaseName} Icon`} />
                    <div><i>{row.description}</i></div>
                    <div className={styles.skill} style={{
                      backgroundColor: skillsJSON.colors.number[row.name],
                      boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number[row.name]}`
                    }}>{row.value}</div>
                  </div>
                  <progress id="file" value={row.value} max={row.maxValue ?? 10} className={styles.attributeBar}
                  style={{accentColor: skillsJSON.colors.bar[row.name as "military" | "oratory" | "loyalty"]}}></progress>
                </div>
              )
            })}
          </div>
          <div className={styles.variableAttributeContainer}>
            <div><div>Influence</div><Image src={InfluenceIcon} height={34} width={34} alt="Influence Icon" /><div>{senator.influence}</div></div>
            <div><div>Talents</div><Image src={TalentsIcon} height={34} width={34} alt="Talents Icon" /><div>{senator.talents}</div></div>
            <div><div>Popularity</div><Image src={PopularityIcon} height={34} width={34} alt="Popularity Icon" /><div>{senator.popularity}</div></div>
            <div><div>Knights</div><Image src={KnightsIcon} height={34} width={34} alt="Knights Icon" /><div>{senator.knights}</div></div>
          </div>
        </div>
      </div>
    )
  } else {
    return null
  }
}

export default SenatorDetails
