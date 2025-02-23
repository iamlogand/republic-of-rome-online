export const formatDate = (isoString: string) => {
  if (isoString == null) return "-"

  const date = new Date(isoString)
  return date.toLocaleString(navigator.language, {
    weekday: "long",
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export const compareDates = (isoStringA: string, isoStringB: string) => {
  return new Date(isoStringA).getTime() - new Date(isoStringB).getTime()
}
