import Image from 'next/image'

import SenatorPortrait from '@/components/SenatorPortrait'
import Collection from '@/classes/Collection'
import Faction from '@/classes/Faction'
import Senator from '@/classes/Senator'
import styles from './FactionListItem.module.css'
import { useGameContext } from '@/contexts/GameContext'
import FactionLink from '@/components/FactionLink'
import SenatorsIcon from "@/images/icons/senators.svg"
import InfluenceIcon from "@/images/icons/influence.svg"
import TalentsIcon from "@/images/icons/talents.svg"
import VotesIcon from "@/images/icons/votes.svg"
import Tooltip from '@mui/material/Tooltip'

type Attribute = {
  name: "senators" | "influence" | "votes" | "talents"
  value: Number
  image: string
  sum?: boolean
}

interface FactionListItemProps {
  faction: Faction
}

// Item in the faction list
const FactionListItem = (props: FactionListItemProps) => {
  const { allPlayers, allSenators } = useGameContext()

  // Get faction-specific data
  const player = allPlayers.byId[props.faction.player] ?? null
  const senators = new Collection<Senator>(
    allSenators.asArray.filter(s => s.faction === props.faction.id).sort((a, b) => a.name.localeCompare(b.name)) ?? []
  )
  const senatorsCount = senators.allIds.length
  const totalInfluence = senators.asArray.reduce((total, senator) => total + senator.influence, 0)
  const totalTalents = senators.asArray.reduce((total, senator) => total + senator.talents, 0)
  const totalVotes = senators.asArray.reduce((total, senator) => total + senator.votes, 0)

  // Attribute data
  const attributeItems: Attribute[] = [
    { name: 'senators', value: senatorsCount, image: SenatorsIcon },
    { name: 'influence', value: totalInfluence, image: InfluenceIcon, sum: true },
    { name: 'talents', value: totalTalents, image: TalentsIcon, sum: true },
    { name: 'votes', value: totalVotes, image: VotesIcon, sum: true }
  ]

  // Get attribute items
  const getAttributeItem = (item: Attribute) => {
    const titleCaseName = item.name[0].toUpperCase() + item.name.slice(1)
    return (
      <Tooltip title={(item.sum ? 'Total' : '') + ` ${titleCaseName}`} enterDelay={500} arrow>
        <div key={item.name} className={`${styles.attribute} ` + (!item.sum ? `${styles.nonSum}` : '')}>
          <div className={styles.symbols}>
            {item.sum && <span className={styles.sigma}>Σ</span>}
            <Image src={item.image} height={34} width={34} alt={`${titleCaseName} icon`} />
          </div>
          <div className={styles.attributeValue}>{item.value.toString()}</div>
        </div>
      </Tooltip>
    )
  }

  if (!player?.user || senators.allIds.length === 0) return null

  return (
    <div className={styles.factionListItem}>
      <p>
        <b><FactionLink faction={props.faction} includeIcon /></b> of {player.user.username}
      </p>
      <div className={styles.attributes}>
        {attributeItems.map(item => getAttributeItem(item))}
      </div>
      <div className={styles.portraits}>
        {senators.asArray.map((senator: Senator) =>
          <SenatorPortrait key={senator.id} senator={senator} size={80} selectable />
        )}
      </div>
    </div>
  )
}

export default FactionListItem