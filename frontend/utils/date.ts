const formatDate = (isoString: string) => {
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

export default formatDate
