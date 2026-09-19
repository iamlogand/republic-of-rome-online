import { expect, test } from "@playwright/test"

import { calculatePersuasion } from "../helpers/persuasion"

const resultForBase = (baseNumber: number, eraEnds = false) =>
  calculatePersuasion({
    oratory: baseNumber,
    influence: 0,
    loyalty: 0,
    targetTalents: 0,
    alignedTarget: false,
    persuaderBribe: 0,
    counterBribes: 0,
    evilOmens: 0,
    eraEnds,
  })

test.describe("persuasion calculation", () => {
  test("applies every modifier to the base number", () => {
    const result = calculatePersuasion({
      oratory: 3,
      influence: 10,
      loyalty: 7,
      targetTalents: 2,
      alignedTarget: true,
      persuaderBribe: 5,
      counterBribes: 3,
      evilOmens: 2,
      eraEnds: false,
    })

    expect(result.baseNumber).toBe(1)
    expect(result.chancePercent).toBe(0)
    expect(result.impossible).toBe(true)
  })

  test("uses the normal automatic-failure limit", () => {
    expect(resultForBase(1)).toMatchObject({
      chancePercent: 0,
      highestSuccessfulRoll: null,
      impossible: true,
    })
    expect(resultForBase(2)).toMatchObject({
      chancePercent: 3,
      highestSuccessfulRoll: 2,
      impossible: false,
    })
    expect(resultForBase(8).chancePercent).toBe(72)
    expect(resultForBase(9)).toMatchObject({
      chancePercent: 83,
      automaticFailureFrom: 10,
      highestSuccessfulRoll: 9,
    })
    expect(resultForBase(10).chancePercent).toBe(83)
    expect(resultForBase(20).chancePercent).toBe(83)
  })

  test("uses the Era Ends automatic-failure limit", () => {
    expect(resultForBase(1, true).chancePercent).toBe(0)
    expect(resultForBase(2, true).chancePercent).toBe(3)
    expect(resultForBase(8, true)).toMatchObject({
      chancePercent: 72,
      automaticFailureFrom: 9,
      highestSuccessfulRoll: 8,
    })
    expect(resultForBase(9, true).chancePercent).toBe(72)
    expect(resultForBase(20, true).chancePercent).toBe(72)
  })
})
