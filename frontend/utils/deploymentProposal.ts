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

export interface DeployedForces {
  legions: number
  veteranLegions: number
  fleets: number
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
 * Example formats:
 * "Deploy {commander} with command of {X} legion(s) ({names}) and {Y} fleet(s) ({names}) to the {war}"
 * "Deploy {X} legion(s) ({names}) and {Y} fleet(s) ({names}) to join {commander}' Campaign in the {war}"
 */
function parseDeploymentProposal(
  proposal: string,
  publicGameState: PublicGameState,
): ParsedProposal | null {
  if (!proposal || !proposal.startsWith("Deploy ")) {
    return null
  }

  // Try to match new deployment format: "Deploy {commander} with command of"
  let commanderMatch = proposal.match(/^Deploy (.+?) with command of/)
  let commanderName = commanderMatch ? commanderMatch[1] : null

  // If not found, try proconsul format: "to join {commander}' Campaign in"
  if (!commanderName) {
    commanderMatch = proposal.match(/to join (.+?)(?:'|'s) Campaign in/)
    commanderName = commanderMatch ? commanderMatch[1] : null
  }

  const commander = commanderName
    ? publicGameState.senators.find(
        (s) => s.displayName === commanderName || s.name === commanderName,
      ) || null
    : null

  // Try "to the {war}" format (new deployment)
  let warMatch = proposal.match(/to the (.+)$/)
  let warName = warMatch ? warMatch[1] : null

  // If not found, try "in the {war}" format (proconsul)
  if (!warName) {
    warMatch = proposal.match(/in the (.+)$/)
    warName = warMatch ? warMatch[1] : null
  }

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
 * Creates a CombatCalculation from a parsed deployment proposal.
 * Includes both the forces mentioned in the proposal AND any forces
 * already deployed (for proconsul deployments or commanderless campaigns).
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

  // Get forces already deployed (proconsul or commanderless campaign)
  const deployed = getDeployedForces(
    publicGameState,
    parsed.commander?.id || null,
    parsed.war?.id || null,
  )

  const isNavalBattle = (parsed.war?.navalStrength ?? 0) > 0

  const calculationData: CombatCalculationData = {
    id: "proposal",
    game: publicGameState.game!.id,
    name: "Current proposal",
    commander: parsed.commander?.id || null,
    war: parsed.war?.id || null,
    land_battle: !isNavalBattle,
    regular_legions: parsed.legions.length + deployed.legions,
    veteran_legions: parsed.veteranLegions.length + deployed.veteranLegions,
    fleets: parsed.fleets.length + deployed.fleets,
  }

  return new CombatCalculation(calculationData)
}

/**
 * Gets the forces already deployed for a commander to a specific war.
 * If the commander is already a proconsul for this war, counts their campaign forces.
 * Otherwise, counts forces from any campaign without a commander to this war
 * (since deploying the commander would make them take control).
 */
export function getDeployedForces(
  publicGameState: PublicGameState,
  commanderId: number | null,
  warId: number | null,
): DeployedForces {
  if (!commanderId || !warId) {
    return { legions: 0, veteranLegions: 0, fleets: 0 }
  }

  // First check if this commander already has a campaign to this war
  const commanderCampaign = publicGameState.campaigns.find(
    (c) => c.commander === commanderId && c.war === warId,
  )

  let campaignToCount

  if (commanderCampaign) {
    // Commander is already a proconsul for this war
    campaignToCount = commanderCampaign
  } else {
    // Commander not yet deployed - check for commanderless campaign
    // they would take control of
    campaignToCount = publicGameState.campaigns.find(
      (c) => c.commander === null && c.war === warId,
    )
  }

  if (!campaignToCount) {
    return { legions: 0, veteranLegions: 0, fleets: 0 }
  }

  // Count forces deployed to the relevant campaign
  const deployedLegions = publicGameState.legions.filter(
    (l) => l.campaign === campaignToCount.id && !l.veteran,
  )
  const deployedVeteranLegions = publicGameState.legions.filter(
    (l) => l.campaign === campaignToCount.id && l.veteran,
  )
  const deployedFleets = publicGameState.fleets.filter(
    (f) => f.campaign === campaignToCount.id,
  )

  return {
    legions: deployedLegions.length,
    veteranLegions: deployedVeteranLegions.length,
    fleets: deployedFleets.length,
  }
}
