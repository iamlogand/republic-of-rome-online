/**
 * Converts a string to its possessive form by adding 's or ' depending on the last letter.
 */
export function toPossessive(str: string): string {
  if (!str || str.length === 0) {
    return str
  }
  if (str.toLowerCase().endsWith("s")) {
    return str + "'"
  }
  return str + "'s"
}

/**
 * Format a list of strings with commas and 'and' before the last item.
 */
export function formatList(items: string[]): string {
  if (items.length === 0) return ""
  if (items.length === 1) return items[0]
  if (items.length === 2) return `${items[0]} and ${items[1]}`
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`
}

/**
 * Capitalize the first letter.
 */
export function toSentenceCase(str: string): string {
  if (!str || str.length === 0) {
    return str
  }
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Converts a Roman family name to its adjectival form.
 */
export function toFamilyAdjective(familyName: string): string {
  if (familyName.endsWith("us")) {
    return familyName.slice(0, -2) + "an"
  }
  return familyName
}
