import PublicGameState from "@/classes/PublicGameState"
import getDiceProbability from "@/helpers/dice"
import { getEvilOmensLevel } from "@/helpers/gameEffects"

const FACTION_LEADER = "faction leader"

export interface PersuasionSenatorSnapshot {
  id: number
  displayName: string
  familyName: string
  faction: number | null
  oratory: number
  influence: number
  loyalty: number
  talents: number
}

export interface PersuasionFactionSnapshot {
  id: number
  displayName: string
}

export interface PersuasionSnapshot {
  persuaders: PersuasionSenatorSnapshot[]
  targets: PersuasionSenatorSnapshot[]
  factions: PersuasionFactionSnapshot[]
  evilOmens: number
  eraEnds: boolean
}

export interface PersuasionCalculationInput {
  oratory: number
  influence: number
  loyalty: number
  targetTalents: number
  alignedTarget: boolean
  persuaderBribe: number
  counterBribes: number
  evilOmens: number
  eraEnds: boolean
}

export interface PersuasionCalculationResult {
  baseNumber: number
  chancePercent: number
  automaticFailureFrom: number
  highestSuccessfulRoll: number | null
  impossible: boolean
}

const snapshotSenator = (
  senator: PublicGameState["senators"][number],
): PersuasionSenatorSnapshot => ({
  id: senator.id,
  displayName: senator.displayName,
  familyName: senator.familyName,
  faction: senator.faction,
  oratory: senator.oratory,
  influence: senator.influence,
  loyalty: senator.loyalty,
  talents: senator.talents,
})

export const createPersuasionSnapshot = (
  publicGameState: PublicGameState,
  factionId: number,
): PersuasionSnapshot => {
  const eligibleSenators = publicGameState.senators.filter(
    (senator) => senator.alive && senator.location === "Rome",
  )
  const byFamilyName = (
    first: PersuasionSenatorSnapshot,
    second: PersuasionSenatorSnapshot,
  ) => first.familyName.localeCompare(second.familyName)

  const persuaders = eligibleSenators
    .filter((senator) => senator.faction === factionId)
    .map(snapshotSenator)
    .sort(byFamilyName)
  const targets = eligibleSenators
    .filter(
      (senator) =>
        senator.faction !== factionId &&
        (senator.faction === null || !senator.titles.includes(FACTION_LEADER)),
    )
    .map(snapshotSenator)
    .sort(byFamilyName)
  return {
    persuaders,
    targets,
    factions: publicGameState.factions
      .filter((faction) => faction.id !== factionId)
      .map((faction) => ({
        id: faction.id,
        displayName: faction.displayName,
      })),
    evilOmens: getEvilOmensLevel(publicGameState.game?.effects ?? []),
    eraEnds: publicGameState.game?.eraEnds ?? false,
  }
}

export const calculatePersuasion = ({
  oratory,
  influence,
  loyalty,
  targetTalents,
  alignedTarget,
  persuaderBribe,
  counterBribes,
  evilOmens,
  eraEnds,
}: PersuasionCalculationInput): PersuasionCalculationResult => {
  const baseNumber =
    oratory +
    influence +
    persuaderBribe +
    evilOmens -
    loyalty -
    targetTalents -
    (alignedTarget ? 7 : 0) -
    counterBribes
  const automaticFailureFrom = eraEnds ? 9 : 10
  const highestSuccessfulRoll = Math.min(baseNumber, automaticFailureFrom - 1)
  const impossible = highestSuccessfulRoll < 2
  const chancePercent = impossible
    ? 0
    : Math.round(getDiceProbability(2, 0, { max: highestSuccessfulRoll }) * 100)

  return {
    baseNumber,
    chancePercent,
    automaticFailureFrom,
    highestSuccessfulRoll: impossible ? null : highestSuccessfulRoll,
    impossible,
  }
}
