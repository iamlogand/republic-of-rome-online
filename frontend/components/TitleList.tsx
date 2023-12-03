import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import Title from "@/classes/Title"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "@/components/TermLink"

const displayOrder = [
  "Dictator",
  "Temporary Rome Consul",
  "Rome Consul",
  "Field Consul",
  "Censor",
  "Master of Horse",
  "HRAO",
  "Prior Consul",
]

interface TitleListProps {
  senator: Senator
  selectable?: boolean
}

// A paragraph listing titles held by a given senator, excluding the Faction Leader title
const TitleList = ({ senator, selectable }: TitleListProps) => {
  const { allTitles } = useGameContext()

  // Get the titles for the senator
  const titles: Collection<Title> = senator
    ? new Collection<Title>(
        allTitles.asArray.filter(
          (t) => t.senator === senator.id && t.name !== "Faction Leader"
        ) ?? new Collection<Title>()
      )
    : new Collection<Title>()
  const titleNames = titles.asArray.map((t) => t.name)

  // Add other titles
  if (senator.rank === 0) titleNames.push("HRAO")

  // Sort the titles
  titleNames.sort((a, b) => {
    const aIndex = displayOrder.indexOf(a)
    const bIndex = displayOrder.indexOf(b)
    if (aIndex === -1 && bIndex === -1) return a.localeCompare(b)
    else if (aIndex === -1) return 1
    else if (bIndex === -1) return -1
    else return aIndex - bIndex
  })

  if (titleNames.length === 0) return null

  return (
    <p>
      {titleNames.map((titleName: string, index: number) => (
        <span key={index}>
          {index > 0 && index < titleNames.length - 1 && ", "}
          {index === titleNames.length - 1 && " and "}
          <TermLink
            name={
              titleName == "Temporary Rome Consul" ? "Rome Consul" : titleName
            }
            displayName={titleName}
            includeIcon
            disabled={!selectable}
          />
        </span>
      ))}
    </p>
  )
}

export default TitleList
