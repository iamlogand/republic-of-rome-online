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
