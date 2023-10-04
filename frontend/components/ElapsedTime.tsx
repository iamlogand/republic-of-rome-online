import { useEffect, useRef, useState } from "react"

const ElapsedTime = ({ resetKey }: { resetKey: number }) => {
  const [seconds, setSeconds] = useState(0)
  const intervalRef = useRef<NodeJS.Timer | null>(null)

  useEffect(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    setSeconds(0)
    intervalRef.current = setInterval(() => {
      setSeconds((prevSeconds) => prevSeconds + 1)
    }, 1000)
  }, [resetKey])

  let formattedTime
  if (seconds === 0) {
    formattedTime = "now"
  } else if (seconds < 60) {
    formattedTime = `${seconds}s ago`
  } else if (seconds < 3600) {
    formattedTime = `${Math.floor(seconds / 60)}m ago`
  } else {
    formattedTime = `${Math.floor(seconds / 3600)}h ago`
  }

  return <span>{formattedTime}</span>
}

export default ElapsedTime
