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
