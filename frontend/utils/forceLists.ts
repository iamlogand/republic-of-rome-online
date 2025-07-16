import Legion from "@/classes/Legion"
import Fleet from "@/classes/Fleet"

// Accepts an array of either Legions or Fleets
export function forceListToString(items: (Legion | Fleet)[]): string {
  if (items.length === 0) return ""

  const groups: (Legion | Fleet)[][] = [[items[0]]]

  for (let i = 1; i < items.length; i++) {
    const item = items[i]
    const lastGroup = groups[groups.length - 1]
    const lastItem = lastGroup[lastGroup.length - 1]

    if (item.number === lastItem.number + 1) {
      lastGroup.push(item)
    } else {
      groups.push([item])
    }
  }

  const groupNames: string[] = []

  for (const group of groups) {
    if (group.length === 1) {
      groupNames.push(group[0].name)
    } else if (group.length === 2) {
      groupNames.push(group[0].name)
      groupNames.push(group[1].name)
    } else {
      groupNames.push(`${group[0].name}-${group[group.length - 1].name}`)
    }
  }

  const joined = groupNames.join(", ")
  const lastComma = joined.lastIndexOf(", ")
  if (lastComma !== -1) {
    return joined.slice(0, lastComma) + " and" + joined.slice(lastComma + 1)
  }

  return joined
}
