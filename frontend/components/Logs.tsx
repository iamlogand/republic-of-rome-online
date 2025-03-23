"use client"

import { useEffect, useState } from "react"

import PublicGameState from "@/classes/PublicGameState"
import Log from "@/classes/Log"
import { compareDates, formatElapsedDate } from "@/utils/date"

interface LogListProps {
  publicGameState: PublicGameState
}

const LogList = ({ publicGameState }: LogListProps) => {
  const [timezone, setTimezone] = useState<string>("")

  useEffect(() => {
    setTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone)
  }, [setTimezone])

  // Update the state to force rendering every 5 seconds
  const [_, setRefreshKey] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => {
      setRefreshKey((oldKey) => oldKey + 1)
    }, 5000)

    return () => {
      clearInterval(interval) // Cleanup on unmount
    }
  }, [])

  return (
    <div className="grow min-h-0 flex flex-col gap-4">
      <h3 className="text-xl mt-4">Logs</h3>
      <div className="border border-neutral-400 rounded flex flex-col overflow-hidden relative">
        <div className="absolute top-0 w-full px-4">
          <div className="w-full h-6 bg-gradient-to-b from-white to-transparent"></div>
        </div>
        <div className="grow min-h-0 overflow-y-auto px-4 py-4 flex flex-col-reverse gap-4">
          {publicGameState?.logs &&
            publicGameState.logs
              .sort((a, b) => {
                const dateComparison = compareDates(b.createdOn, a.createdOn)
                if (dateComparison !== 0) {
                  return dateComparison
                }
                return a.id - b.id
              })
              .map((log: Log, index: number) => {
                return (
                  <div
                    key={index}
                    className="flex flex-col gap-x-4 items-baseline"
                  >
                    <div className="w-full flex gap-x-4 text-sm justify-between">
                      <div className="flex gap-x-2">
                        <div className="text-neutral-600 whitespace-nowrap">
                          Turn {log.turn}
                        </div>
                        <div className="text-neutral-600 whitespace-nowrap">
                          {log.phase} phase
                        </div>
                      </div>
                      <div className="text-neutral-600 whitespace-nowrap">
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
