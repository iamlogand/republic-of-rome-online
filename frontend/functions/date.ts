import { utcToZonedTime } from "date-fns-tz"

const formatDate = (date: Date, timezone: string) => {
  const zonedDate = utcToZonedTime(date, timezone)

  const year = zonedDate.getFullYear()
  const month = ("0" + (zonedDate.getMonth() + 1)).slice(-2)
  const day = ("0" + zonedDate.getDate()).slice(-2)
  const hour = ("0" + zonedDate.getHours()).slice(-2)
  const minute = ("0" + zonedDate.getMinutes()).slice(-2)

  return `${year}-${month}-${day} ${hour}:${minute}`
}

export const formatElapsedDate = (date: Date, timezone: string) => {
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

export default formatDate
