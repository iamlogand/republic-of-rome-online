import Collection from "@/classes/Collection"
import Senator from "@/classes/Senator"
import Title from "@/classes/Title"
import { useGameContext } from "@/contexts/GameContext"
import TermLink from "@/components/TermLink"

const nonTerms = ["Dead Senator"]

const displayOrder = [
  "Dead Senator",
  "HRAO",
  "Dictator",
  "Temporary Rome Consul",
  "Rome Consul",
  "Field Consul",
  "Censor",
  "Master of Horse",
  "Prior Consul",
  "Senator",
]

interface SenatorFactListProps {
  senator: Senator
  selectable?: boolean
}

// A paragraph listing titles held by a given senator, excluding the Faction Leader title
const SenatorFactList = ({ senator, selectable }: SenatorFactListProps) => {
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

  // Add other facts
  if (senator.rank !== null && senator.rank <= 0) titleNames.push("HRAO")
  if (!senator.alive) {
    titleNames.push("Dead Senator")
  } else {
    titleNames.push("Senator")
  }

  // Sort the items
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
      {titleNames.map((titleName: string, index: number) => {
        if (titleName === "Dead Senator") {
          if (titleNames.length > 1) {
            return (
              <span key={index}>
                Dead <TermLink name="Senator" disabled={!selectable} />, was{" "}
              </span>
            )
          } else {
            return (
              <span key={index}>
                Dead <TermLink name="Senator" disabled={!selectable} />
              </span>
            )
          }
        }
        return (
          <span key={index}>
            {nonTerms.includes(titleName) ? (
              <span key={index}>{titleName}</span>
            ) : (
              <TermLink
                name={
                  titleName == "Temporary Rome Consul"
                    ? "Rome Consul"
                    : titleName
                }
                displayName={titleName}
                includeIcon
                disabled={!selectable}
              />
            )}
            <span>
              {index < titleNames.length - 2 && ", "}
              {index === titleNames.length - 2 &&
                titleNames.length > 1 &&
                " and "}
            </span>
          </span>
        )
      })}
    </p>
  )
}

export default SenatorFactList
