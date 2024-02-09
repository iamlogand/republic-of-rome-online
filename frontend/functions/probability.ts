const getDiceRollProbability = (
  dice_count: number,
  target_numbers: number[]
) => {
  // Work out the probability of a dice roll hitting any of the target numbers
  const dice_sides = [1, 2, 3, 4, 5, 6]
  let outcomes = [1, 2, 3, 4, 5, 6]
  for (let dice_index = 1; dice_index < dice_count; dice_index++) {
    let next_set_of_outcomes: number[] = []
    outcomes.forEach((outcome) => {
      for (let side_index = 0; side_index < dice_sides.length; side_index++) {
        next_set_of_outcomes.push(outcome + dice_sides[side_index])
      }
    })
    outcomes = next_set_of_outcomes
  }
  let match_count = 0
  outcomes.forEach((outcome) => {
    if (target_numbers.includes(outcome)) {
      match_count += 1
    }
  })
  const probability =
    match_count === 1 ? 1 : Math.round((match_count / outcomes.length) * 100)
  return `${probability}%`
}

export default getDiceRollProbability
