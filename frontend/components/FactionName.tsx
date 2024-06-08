import Faction from "@/classes/Faction"

interface FactionNameProps {
  faction: Faction
  maxWidth?: number
}

// Faction name contained in a span, unless `maxWidth` is specified, in which case it is contained in a div.
const FactionName = ({ faction, maxWidth }: FactionNameProps) => {
  if (!faction) return null

  if (faction.customName) {
    if (maxWidth) {
      return (
        <div
          className="text-nowrap overflow-hidden text-ellipsis"
          style={{ maxWidth: maxWidth }}
        >
          {faction.customName}
        </div>
      )
    } else {
      const longestWord = faction.customName
        .split(" ")
        .reduce((a, b) => (a.length > b.length ? a : b))
      // Only break all if the longest word in the name is longer than 11 characters (less than 1% of words in the English language are this long)
      if (longestWord.length > 11) {
        return <span className="break-all">{faction.customName}</span>
      } else {
        return <span>{faction.customName}</span>
      }
    }
  } else {
    return <span>{faction.getName()} Faction</span>
  }
}

export default FactionName
