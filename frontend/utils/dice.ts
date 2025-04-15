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
  target_options: { min?: number; exact?: number },
) => {
  // Validation
  if (target_options) {
    const providedKeys = Object.keys(target_options)
    if (providedKeys.length > 1) {
      throw new Error("You can provide only one target option.")
    }
  }

  let probabilityTable = diceProbabilityTable[dice]
  let totalProbability = 0
  for (const [key, probability] of Object.entries(probabilityTable)) {
    const modifiedResult = Number(key) + modifier
    if (
      target_options.min !== undefined &&
      modifiedResult >= target_options.min
    ) {
      totalProbability += probability
    }
    if (
      target_options.exact !== undefined &&
      modifiedResult === target_options.exact
    ) {
      totalProbability += probability
    }
  }
  return totalProbability
}

export default getDiceProbability
