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
import Title from '@/classes/Title'

type FixedAttribute = {
  name: "military" | "oratory" | "loyalty"
  value: number
  maxValue?: number
  image: string
  description: string
}

type VariableAttribute = {
  name: "influence" | "talents" | "popularity" | "knights" | "votes"
  value: number
  image: string
}

type NormalSkillValue = 1 | 2 | 3 | 4 | 5 | 6
type LoyaltySkillValue = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10

interface SenatorDetailsProps {
  detailSectionRef: RefObject<HTMLDivElement>
}

// Detail section content for a senator
const SenatorDetails = (props: SenatorDetailsProps) => {
  const { allPlayers, allFactions, allSenators, allTitles, selectedEntity } = useGameContext()
  
  // Get senator-specific data
  const senator: Senator | null = selectedEntity?.id ? allSenators.byId[selectedEntity.id] ?? null : null
  const faction: Faction | null = senator?.faction ? allFactions.byId[senator.faction] ?? null : null
  const player: Player | null = faction?.player ? allPlayers.byId[faction.player] ?? null : null
  const majorOffice: Title | null = senator ? allTitles.asArray.find(o => o.senator === senator.id && o.major_office == true) ?? null : null
  const factionLeader: boolean = senator ? allTitles.asArray.some(o => o.senator === senator.id && o.name == 'Faction Leader') : false

  // Calculate senator portrait size.
  // Image size must be defined in JavaScript rather than in CSS
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

  // Fixed attribute data
  const fixedAttributeItems: FixedAttribute[] = senator ? [
    {
      name: 'military', value: senator.military, maxValue: 6, image: MilitaryIcon,
      description: `${skillsJSON.descriptions.default[senator.military as NormalSkillValue]} Commander`
    },
    {
      name: 'oratory', value: senator.oratory, maxValue: 6, image: OratoryIcon,
      description: `${skillsJSON.descriptions.default[senator.oratory as NormalSkillValue]} Orator`
    },
    {
      name: 'loyalty', value: senator.loyalty, image: LoyaltyIcon,
      description: `${skillsJSON.descriptions.loyalty[senator.loyalty as LoyaltySkillValue]}`
    }
  ] : []

  // Variable attribute data
  const variableAttributeItems: VariableAttribute[] = senator ? [
    { name: 'influence', value: senator.influence, image: InfluenceIcon },
    { name: 'talents', value: senator.talents, image: TalentsIcon },
    { name: 'popularity', value: senator.popularity, image: PopularityIcon },
    { name: 'knights', value: senator.knights, image: KnightsIcon },
    { name: 'votes', value: senator.votes, image: VotesIcon }
  ] : []

  // Get JSX for a fixed attribute item
  const getFixedAttributeRow = (item: FixedAttribute) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <div key={item.name} className={styles.attribute}>
        <div className={styles.attributeNameAndValue}>
          <div>
            {titleCaseName}
          </div>
          <Image src={item.image} height={34} width={34} alt={`${titleCaseName} Icon`} />
          <div><i>{item.description}</i></div>
          <div
            className={styles.skill}
            style={{
              backgroundColor: skillsJSON.colors.number[item.name],
              boxShadow: `0px 0px 2px 2px ${skillsJSON.colors.number[item.name]}`
            }}
          >{item.value}</div>
        </div>
        <progress
          id="file"
          value={item.value}
          max={item.maxValue ?? 10}
          className={styles.attributeBar}
          style={{ accentColor: skillsJSON.colors.bar[item.name as "military" | "oratory" | "loyalty"] }}
        />
      </div>
    )
  }

  // Get JSX for a variable attribute item
  const getVariableAttributeRow = (item: VariableAttribute) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <div>
        <div>{item.name}</div>
        <Image src={item.image} height={34} width={34} alt={`${titleCaseName} Icon`} />
        <div>{item.value}</div>
      </div>
    )
  }
  
  // If there is no senator selected, render nothing
  if (!senator) return null
    
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
          {fixedAttributeItems.map(item => getFixedAttributeRow(item))}
        </div>
        <div className={styles.variableAttributeContainer}>
          {variableAttributeItems.map(item => getVariableAttributeRow(item))}
        </div>
      </div>
    </div>
  )
}

export default SenatorDetails
