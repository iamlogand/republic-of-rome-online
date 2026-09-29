import getDiceProbability from "@/helpers/dice"

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
