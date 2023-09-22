import Image from 'next/image'
import { RefObject, useEffect, useState } from "react"

import SenatorPortrait from "@/components/SenatorPortrait"
import Senator from "@/classes/Senator"
import Player from "@/classes/Player"
import Faction from "@/classes/Faction"
import styles from "./DetailSection_Senator.module.css"
import { useGameContext } from "@/contexts/GameContext"
import skillsJSON from "@/data/skills.json"
import MilitaryIcon from "@/images/icons/military.svg"
import OratoryIcon from "@/images/icons/oratory.svg"
import LoyaltyIcon from "@/images/icons/loyalty.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import PopularityIcon from "@/images/icons/popularity.svg"
import KnightsIcon from "@/images/icons/knights.svg"
import VotesIcon from "@/images/icons/votes.svg"
import FactionLink from '@/components/FactionLink'

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
  
  const senator: Senator | null = selectedEntity?.id ? allSenators.byId[selectedEntity.id] ?? null : null
  const faction: Faction | null = senator?.faction ? allFactions.byId[senator.faction] ?? null : null
  const player: Player | null = faction?.player ? allPlayers.byId[faction.player] ?? null : null

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
  
  if (senator) {
    const majorOffice = allTitles.asArray.find(o => o.senator === senator.id && o.major_office == true) ?? null
    const factionLeader: boolean = allTitles.asArray.some(o => o.senator === senator.id && o.name == 'Faction Leader')

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
      <div className={styles.senatorDetailSection}>
        <div className={styles.primaryArea}>
          <div className={styles.portraitContainer}><SenatorPortrait senator={senator} size={getPortraitSize()} /></div>
          <div className={styles.textContainer}>
            <p><b>{senator.displayName}</b></p>
            <p>
              {faction ?
                <span>
                  <FactionLink faction={faction} includeIcon />
                  {factionLeader ? ' Leader' : null}
                  {player ? <span> ({player.user?.username})</span> : null}
                </span>
                :
                (senator.alive ? 'Unaligned' : 'Dead')
              }
            </p>
            {majorOffice && <p>Serving as <b>{majorOffice?.name}</b></p>}
          </div>
        </div>
        <div className={styles.attributeArea}>
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
                  style={{ accentColor: skillsJSON.colors.bar[row.name as "military" | "oratory" | "loyalty"] }}></progress>
                </div>
              )
            })}
          </div>
          <div className={styles.variableAttributeContainer}>
            <div><div>Influence</div><Image src={InfluenceIcon} height={34} width={34} alt="Influence Icon" /><div>{senator.influence}</div></div>
            <div><div>Talents</div><Image src={TalentsIcon} height={34} width={34} alt="Talents Icon" /><div>{senator.talents}</div></div>
            <div><div>Popularity</div><Image src={PopularityIcon} height={34} width={34} alt="Popularity Icon" /><div>{senator.popularity}</div></div>
            <div><div>Knights</div><Image src={KnightsIcon} height={34} width={34} alt="Knights Icon" /><div>{senator.knights}</div></div>
            <div><div>Votes</div><Image src={VotesIcon} height={34} width={34} alt="Votes Icon" /><div>{senator.votes}</div></div>
          </div>
        </div>
      </div>
    )
  } else {
    return null
  }
}

export default SenatorDetails
