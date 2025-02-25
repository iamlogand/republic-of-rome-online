type ProbabilityTable = {
  [key: number]: number
}

const probabilityTable1d6: ProbabilityTable = {
  1: 1 / 6,
  2: 1 / 6,
  3: 1 / 6,
  4: 1 / 6,
  5: 1 / 6,
  6: 1 / 6,
}

const getDiceProbability = (
  dice: 1 | 2 | 3,
  modifier: number,
  target_min: number
) => {
  let probabilityTable = probabilityTable1d6
  // TODO support 2d6 and 3d6
  // TODO support other types of target, e.g. specific numbers

  let totalProbability = 0
  for (let result in probabilityTable) {
    const modifiedResult = Number(result) + modifier
    if (modifiedResult >= Number(target_min)) {
      totalProbability += probabilityTable[result]
    }
  }
  return totalProbability
}

export default getDiceProbability
