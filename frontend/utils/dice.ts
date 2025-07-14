const diceProbabilityTable = {
  1: {
    1: 1 / 6,
    2: 1 / 6,
    3: 1 / 6,
    4: 1 / 6,
    5: 1 / 6,
    6: 1 / 6,
  },
  2: {
    2: 1 / 36,
    3: 2 / 36,
    4: 3 / 36,
    5: 4 / 36,
    6: 5 / 36,
    7: 6 / 36,
    8: 5 / 36,
    9: 4 / 36,
    10: 3 / 36,
    11: 2 / 36,
    12: 1 / 36,
  },
  3: {
    3: 1 / 216,
    4: 3 / 216,
    5: 6 / 216,
    6: 10 / 216,
    7: 15 / 216,
    8: 21 / 216,
    9: 25 / 216,
    10: 27 / 216,
    11: 27 / 216,
    12: 25 / 216,
    13: 21 / 216,
    14: 15 / 216,
    15: 10 / 216,
    16: 6 / 216,
    17: 3 / 216,
    18: 1 / 216,
  },
}

const getDiceProbability = (
  dice: 1 | 2 | 3,
  modifier: number,
  target_options: { min?: number; max?: number; exacts?: number[] },
  ignored_numbers: number[] = [],
) => {
  let probabilityTable = diceProbabilityTable[dice]
  let totalProbability = 0
  for (const [key, probability] of Object.entries(probabilityTable)) {
    // Using unmodified result
    const result = Number(key)
    if (ignored_numbers && ignored_numbers.includes(result)) continue
    if (
      target_options.exacts !== undefined &&
      target_options.exacts.includes(result)
    ) {
      totalProbability += probability
    }

    // Using modified result
    const modifiedResult = result + modifier
    if (
      target_options.min !== undefined &&
      target_options.max === undefined &&
      modifiedResult >= target_options.min
    ) {
      totalProbability += probability
    } else if (
      target_options.max !== undefined &&
      target_options.min === undefined &&
      modifiedResult <= target_options.max
    ) {
      totalProbability += probability
    } else if (
      target_options.max !== undefined &&
      target_options.min !== undefined &&
      modifiedResult >= target_options.min &&
      modifiedResult <= target_options.max
    ) {
      totalProbability += probability
    }
  }
  return totalProbability
}

export default getDiceProbability
