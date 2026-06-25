/**
 * Parses a game effect string of the form "effect name" or "effect name:level"
 * and returns the base name and level.
 */
export const parseEffectString = (
  effect: string,
): { baseName: string; level: number } => {
  const colonIndex = effect.indexOf(":")
  return {
    baseName: colonIndex >= 0 ? effect.slice(0, colonIndex) : effect,
    level: colonIndex >= 0 ? parseInt(effect.slice(colonIndex + 1), 10) : 1,
  }
}

/**
 * Returns the current evil omens level from a game effects array.
 * Returns 0 if evil omens is not active.
 */
export const getEvilOmensLevel = (effects: string[]): number => {
  for (const effect of effects) {
    const { baseName, level } = parseEffectString(effect)
    if (baseName === "evil omens") return level
  }
  return 0
}
