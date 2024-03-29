const getNumberSuffix = (number: number) => {
  if (number === 1) return "st"
  if (number === 2) return "nd"
  if (number === 3) return "rd"
  return "th"
}

export default getNumberSuffix
