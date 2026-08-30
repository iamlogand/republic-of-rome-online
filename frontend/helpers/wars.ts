import EnemyLeader from "@/classes/EnemyLeader"
import War from "@/classes/War"

// Wars are ordered by how much attention they demand, so that the ones
// threatening Rome right now appear before the ones that don't
const STATUS_ORDER: Record<War["status"], number> = {
  active: 0,
  imminent: 1,
  inactive: 2,
  defeated: 3,
}

export function compareWars(a: War, b: War): number {
  return STATUS_ORDER[a.status] - STATUS_ORDER[b.status] || a.id - b.id
}

// Every active war in the same numbered series, including the war itself.
// Matching wars multiply each other's strength (§1.07.332)
export function getMatchingWars(war: War, wars: War[]): War[] {
  if (!war.seriesName) return []
  return wars
    .filter((w) => w.seriesName === war.seriesName && w.status === "active")
    .sort((a, b) => a.index - b.index)
}

// Only active leaders add their strength to a war (§1.07.342). A leader drawn
// while no matching war is active waits in the Forum, and leaders withdraw once
// their last matching war is defeated
export function getActiveLeaders(
  war: War,
  enemyLeaders: EnemyLeader[],
): EnemyLeader[] {
  if (!war.seriesName) return []
  return enemyLeaders.filter((l) => l.active && l.seriesName === war.seriesName)
}

export interface WarStrengthBreakdown {
  // The unmodified strength printed on the war card
  base: number
  // 1 to 4, from the number of active matching wars (§1.07.332)
  multiplier: number
  matchingWars: War[]
  leaders: EnemyLeader[]
  leaderStrength: number
  total: number
  isModified: boolean
}

// Land and fleet strength are multiplied by matching wars and then increased by
// leader strength (§1.07.342). Fleet support is never modified
export function getWarStrengthBreakdown(
  war: War,
  battle: "land" | "naval",
  wars: War[],
  enemyLeaders: EnemyLeader[],
): WarStrengthBreakdown {
  const base = battle === "land" ? war.landStrength : war.navalStrength
  const matchingWars = getMatchingWars(war, wars)
  const multiplier = Math.max(1, matchingWars.length)
  const leaders = getActiveLeaders(war, enemyLeaders)
  const leaderStrength = leaders.reduce((sum, l) => sum + l.strength, 0)
  return {
    base,
    multiplier,
    matchingWars,
    leaders,
    leaderStrength,
    total: base * multiplier + leaderStrength,
    isModified: multiplier > 1 || leaderStrength > 0,
  }
}
