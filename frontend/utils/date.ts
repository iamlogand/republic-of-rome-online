import { utcToZonedTime } from "date-fns-tz"

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

export const formatElapsedDate = (isoString: string, timezone: string) => {
  const date = new Date(isoString)
  const zonedDate = utcToZonedTime(date, timezone)
  const now = new Date()
  const elapsed = now.getTime() - zonedDate.getTime()

  const seconds = Math.floor(elapsed / 1000)
  const minutes = Math.floor(seconds / 60)
  if (minutes < 1) {
    return "Now"
  }
  const hours = Math.floor(minutes / 60)
  if (hours < 1) {
    return `${minutes} ${minutes === 1 ? "min" : "mins"} ago`
  }
  const days = Math.floor(hours / 24)
  if (days < 1) {
    return `${hours} ${hours === 1 ? "hour" : "hours"} ago`
  }
  const weeks = Math.floor(days / 7)
  if (weeks < 1) {
    return `${days} ${days === 1 ? "day" : "days"} ago`
  }
  const months = Math.floor(days / 30)
  if (months < 1) {
    return `${weeks} ${weeks === 1 ? "week" : "weeks"} ago`
  }
  const years = Math.floor(days / 365)
  if (years < 1) {
    return `${months} ${months === 1 ? "month" : "months"} ago`
  }
  return `${years} ${years === 1 ? "year" : "years"} ago`
}
