"use client"

import { useEffect, useState } from "react"

import Log from "@/classes/Log"
import PublicGameState from "@/classes/PublicGameState"
import { formatElapsedDate } from "@/utils/date"

interface LogListProps {
  publicGameState: PublicGameState
}

const LogList = ({ publicGameState }: LogListProps) => {
  const [timezone, setTimezone] = useState<string>("")

  useEffect(() => {
    setTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone)
  }, [setTimezone])

  // Update the state to force rendering every 5 seconds
  const [, setRefreshKey] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshKey((oldKey) => oldKey + 1)
    }, 5000)

    return () => {
      clearInterval(interval)
    }
  }, [])

  return (
    <div className="flex min-h-0 grow flex-col gap-4">
      <h3 className="mt-4 text-xl">Logs</h3>
      <div className="relative flex flex-col overflow-hidden rounded border border-neutral-400">
        <div className="absolute top-0 w-full px-4">
          <div className="h-6 w-full bg-gradient-to-b from-white to-transparent"></div>
        </div>
        <div className="flex min-h-0 grow flex-col-reverse gap-4 overflow-y-auto px-4 py-4">
          {publicGameState?.logs &&
            publicGameState.logs
              .sort((a, b) => {
                return b.id - a.id
              })
              .map((log: Log, index: number) => {
                return (
                  <div
                    key={index}
                    className="flex flex-col items-baseline gap-x-4"
                  >
                    <div className="flex w-full justify-between gap-x-4 text-sm">
                      <div className="flex gap-x-2">
                        <div className="whitespace-nowrap text-neutral-600">
                          Turn {log.turn}
                        </div>
                        <div className="whitespace-nowrap text-neutral-600">
                          {log.phase} phase
                        </div>
                      </div>
                      <div className="whitespace-nowrap text-neutral-600">
                        {formatElapsedDate(log.createdOn, timezone)}
                      </div>
                    </div>
                    <div>{log.text}</div>
                  </div>
                )
              })}
        </div>
      </div>
    </div>
  )
}

export default LogList
