"use client"

import { useEffect, useState } from "react"

import Log from "@/classes/Log"
import PublicGameState from "@/classes/PublicGameState"
import { formatElapsedDate } from "@/helpers/date"

interface Props {
  publicGameState: PublicGameState
}

const LogList = ({ publicGameState }: Props) => {
  const [timezone, setTimezone] = useState<string>("")

  useEffect(() => {
    setTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone)
  }, [setTimezone])

  // Force re-render every 5 seconds to keep elapsed times fresh
  const [, setRefreshKey] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => setRefreshKey((k) => k + 1), 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex shrink-0 flex-col overflow-hidden border-l border-neutral-300" style={{ width: "clamp(485px, calc(100vw - 795px), 600px)" }}>
      <div className="flex min-h-0 grow flex-col-reverse gap-4 overflow-y-auto px-10 py-4">
        {publicGameState.logs
          .sort((a, b) => b.id - a.id)
          .map((log: Log, index: number) => (
            <div key={index} className="flex flex-col items-baseline gap-x-4">
              <div className="flex w-full justify-between gap-x-4 text-sm">
                <div className="flex gap-x-2">
                  <div className="whitespace-nowrap text-neutral-600">
                    Turn {log.turn}
                  </div>
                  <div className="whitespace-nowrap capitalize text-neutral-600">
                    {log.phase} phase
                  </div>
                </div>
                <div className="whitespace-nowrap text-neutral-600">
                  {formatElapsedDate(log.createdOn, timezone)}
                </div>
              </div>
              <div>{log.text}</div>
            </div>
          ))}
      </div>
    </div>
  )
}

export default LogList
