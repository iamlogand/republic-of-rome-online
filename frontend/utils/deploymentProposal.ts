import CombatCalculation, {
  CombatCalculationData,
} from "@/classes/CombatCalculation"
import Fleet from "@/classes/Fleet"
import Legion from "@/classes/Legion"
import PublicGameState from "@/classes/PublicGameState"
import Senator from "@/classes/Senator"
import War from "@/classes/War"

interface ParsedProposal {
  commander: Senator | null
  war: War | null
  legions: Legion[]
  veteranLegions: Legion[]
  fleets: Fleet[]
}

/**
 * Parses unit names string (e.g., "I–V and VII" or "I, II and IV") into array of unit objects
 */
function parseUnitNames<T extends Legion | Fleet>(
  namesString: string,
  availableUnits: T[],
): T[] {
  if (!namesString || namesString.trim() === "") {
    return []
  }

  const groups = namesString.replace(/ and /g, ", ").split(", ")
  const units: T[] = []

  for (const group of groups) {
    if (group.includes("–")) {
      // Handle range (e.g., "I–V")
      const [startName, endName] = group.split("–")
      const startUnit = availableUnits.find((u) => u.name === startName.trim())
      const endUnit = availableUnits.find((u) => u.name === endName.trim())

      if (startUnit && endUnit) {
        for (let num = startUnit.number; num <= endUnit.number; num++) {
          const unit = availableUnits.find((u) => u.number === num)
          if (unit && !units.includes(unit)) {
            units.push(unit)
          }
        }
      }
    } else {
      // Handle single name (e.g., "I")
      const unit = availableUnits.find((u) => u.name === group.trim())
      if (unit && !units.includes(unit)) {
        units.push(unit)
      }
    }
  }

  return units
}

/**
 * Parses a deployment proposal string into structured data
 * Format: "Deploy {commander} with command of {X} legion(s) ({names}) and {Y} fleet(s) ({names}) to the {war}"
 */
function parseDeploymentProposal(
  proposal: string,
  publicGameState: PublicGameState,
): ParsedProposal | null {
  if (!proposal || !proposal.startsWith("Deploy ")) {
    return null
  }

  const commanderMatch = proposal.match(/^Deploy (.+?) with command of/)
  const commanderName = commanderMatch ? commanderMatch[1] : null
  const commander = commanderName
    ? publicGameState.senators.find(
        (s) => s.displayName === commanderName || s.name === commanderName,
      ) || null
    : null

  const warMatch = proposal.match(/to the (.+)$/)
  const warName = warMatch ? warMatch[1] : null
  const war = warName
    ? publicGameState.wars.find((w) => w.name === warName) || null
    : null

  let legions: Legion[] = []
  let veteranLegions: Legion[] = []
  const legionMatch = proposal.match(/(\d+) legions? \(([^)]+)\)(?: and)?/)
  if (legionMatch) {
    const legionNames = legionMatch[2]
    const allLegions = parseUnitNames(legionNames, publicGameState.legions)
    legions = allLegions.filter((l) => !l.veteran)
    veteranLegions = allLegions.filter((l) => l.veteran)
  }

  let fleets: Fleet[] = []
  const fleetMatch = proposal.match(/(\d+) fleets? \(([^)]+)\)/)
  if (fleetMatch) {
    const fleetNames = fleetMatch[2]
    fleets = parseUnitNames(fleetNames, publicGameState.fleets)
  }

  return {
    commander,
    war,
    legions,
    veteranLegions,
    fleets,
  }
}

/**
 * Creates a CombatCalculation from a parsed deployment proposal
 */
export function createProposalCalculation(
  publicGameState: PublicGameState,
): CombatCalculation | null {
  const proposal = publicGameState.game?.currentProposal
  if (!proposal || !proposal.startsWith("Deploy ")) {
    return null
  }

  const parsed = parseDeploymentProposal(proposal, publicGameState)
  if (!parsed) {
    return null
  }

  const isNavalBattle = (parsed.war?.navalStrength ?? 0) > 0

  const calculationData: CombatCalculationData = {
    id: "proposal",
    game: publicGameState.game!.id,
    name: "Current proposal",
    commander: parsed.commander?.id || null,
    war: parsed.war?.id || null,
    land_battle: !isNavalBattle,
    legions: parsed.legions.length,
    veteran_legions: parsed.veteranLegions.length,
    fleets: parsed.fleets.length,
  }

  return new CombatCalculation(calculationData)
}
