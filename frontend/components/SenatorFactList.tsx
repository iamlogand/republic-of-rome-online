import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import Title from "@/classes/Title"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "@/components/TermLink"

const TITLE_DISPLAY_ORDER = [
  "HRAO",
  "Dictator",
  "Temporary Rome Consul",
  "Rome Consul",
  "Field Consul",
  "Censor",
  "Master of Horse",
  "Prior Consul",
]

type SenatorFactListItem = {
  name: string
  jsx?: JSX.Element
  customSeparator?: JSX.Element // Custom separator to follow the item instead of the default ", " or " and "
}

interface SenatorFactListProps {
  senator: Senator
  selectable?: boolean
}

// A paragraph listing titles held by a given senator, excluding the Faction Leader title
const SenatorFactList = ({ senator, selectable }: SenatorFactListProps) => {
  const { allTitles, allConcessions } = useGameContext()

  if (!senator) return null

  // Get the senator's titles
  const titles = allTitles.asArray.filter(
    (t) => t.senator === senator.id && t.name !== "Faction Leader"
  )
  const items: SenatorFactListItem[] = titles.map((t) => {
    return {
      name: t.name,
      jsx: <TermLink name={t.name} disabled={!selectable} includeIcon />,
    }
  })

  // Sort the titles
  items.sort((a, b) => {
    const aIndex = TITLE_DISPLAY_ORDER.indexOf(a.name)
    const bIndex = TITLE_DISPLAY_ORDER.indexOf(b.name)
    if (aIndex === -1 && bIndex === -1) return a.name.localeCompare(b.name)
    else if (aIndex === -1) return 1
    else if (bIndex === -1) return -1
    else return aIndex - bIndex
  })

  // Get the senator's concessions
  const concessions = allConcessions.asArray.filter(
    (c) => c.senator === senator.id
  )
  concessions.forEach((c) => {
    items.push({
      name: c.name
    })
  })

  // Fix the Temporary Rome Consul title
  const tempRomeConsulIndex = items.find(
    (item) => item.name === "Temporary Rome Consul"
  )
  if (tempRomeConsulIndex) {
    tempRomeConsulIndex.jsx = (
      <TermLink
        name="Rome Consul"
        displayName="Temporary Rome Consul"
        disabled={!selectable}
        includeIcon
      />
    )
  }

  // Add HRAO
  if (senator.rank !== null && senator.rank <= 0)
    items.unshift({
      name: "HRAO",
      jsx: <TermLink name="HRAO" disabled={!selectable} includeIcon />,
    })

  // Add Dead Senator or Senator
  if (!senator.alive) {
    items.unshift({
      name: "Dead Senator",
      jsx: (
        <span>
          Dead <TermLink name="Senator" disabled={!selectable} />
        </span>
      ),
      customSeparator: items.length > 0 ? <span>, was </span> : undefined,
    })
  } else {
    items.push({
      name: "Senator",
      jsx: <TermLink name="Senator" disabled={!selectable} includeIcon />,
    })
  }

  if (items.length === 0) return null

  const renderSeparator = (index: number) => (
    <span>
      {index < items.length - 2 && ", "}
      {index === items.length - 2 && items.length > 1 && " and "}
    </span>
  )

  return (
    <p>
      {items.map((item: SenatorFactListItem, index: number) => (
        <span key={index}>
          {item.jsx ?? item.name}
          {item.customSeparator ? item.customSeparator : renderSeparator(index)}
        </span>
      ))}
    </p>
  )
}

export default SenatorFactList
