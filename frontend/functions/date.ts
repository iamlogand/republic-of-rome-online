import { utcToZonedTime } from "date-fns-tz"

const formatDate = (date, timezone) => {
  const zonedDate = utcToZonedTime(date, timezone)

  const year = zonedDate.getFullYear()
  const month = ("0" + (zonedDate.getMonth() + 1)).slice(-2)
  const day = ("0" + zonedDate.getDate()).slice(-2)
  const hour = ("0" + zonedDate.getHours()).slice(-2)
  const minute = ("0" + zonedDate.getMinutes()).slice(-2)

  return `${year}-${month}-${day} ${hour}:${minute}`
}

export const formatElapsedDate = (date, timezone) => {
  const zonedDate = utcToZonedTime(date, timezone)
  const now = new Date()
  const elapsed = now.getTime() - zonedDate.getTime()

  const seconds = Math.floor(elapsed / 1000)
  if (seconds < 60) {
    return "Now"
  }

  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) {
    if (minutes === 1) {
      return `1 min ago`
    } else {
      return `${minutes} mins ago`
    }
  }

  const hours = Math.floor(minutes / 60)
  if (hours < 24) {
    if (hours === 1) {
      return `1 hour ago`
    } else {
      return `${hours} hours ago`
    }
  }

  const days = Math.floor(hours / 24)
  if (days < 7) {
    if (days == 1) {
      return `1 day ago`
    } else {
      return `${days} days ago`
    }
  }

  const weeks = Math.floor(days / 7)
  if (weeks < 4) {
    if (weeks === 1) {
      return `1 week ago`
    } else {
      return `${weeks} weeks ago`
    }
  }

  const months = Math.floor(days / 30)
  if (months < 12) {
    if (months === 1) {
      return `1 month ago`
    } else {
      return `${months} months ago`
    }
  }

  const years = Math.floor(days / 365)
  if (years === 1) {
    return `1 year ago`
  } else {
    return `${years} years ago`
  }
}

export default formatDate
