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

export default formatDate
