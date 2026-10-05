"use client"

import { useEffect, useRef, useState } from "react"

import Log from "@/classes/Log"
import PublicGameState from "@/classes/PublicGameState"
import { formatElapsedDate } from "@/helpers/date"
import useTrackedIds from "@/hooks/useTrackedIds"

interface Props {
  publicGameState: PublicGameState
}

const LogList = ({ publicGameState }: Props) => {
  const [timezone, setTimezone] = useState<string>("")
  const scrollRef = useRef<HTMLDivElement>(null)
  const isAtBottomRef = useRef(true)

  const gameId = publicGameState.game?.id
  const gameFinished = publicGameState.game?.status === "finished"
  const seen = useTrackedIds("seen-logs", gameId, gameFinished)
  const acknowledged = useTrackedIds("acknowledged-logs", gameId, gameFinished)

  useEffect(() => {
    setTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone)
  }, [setTimezone])

  // Force re-render every 5 seconds to keep elapsed times fresh
  const [, setRefreshKey] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => setRefreshKey((k) => k + 1), 5000)
    return () => clearInterval(interval)
  }, [])

  // Scroll to bottom when logs change, only if user hasn't scrolled up
  useEffect(() => {
    const el = scrollRef.current
    if (el && isAtBottomRef.current) {
      el.scrollTop = el.scrollHeight
    }
  }, [publicGameState.logs])

  // Mark logs as seen after each render
  useEffect(() => {
    const currentIds = publicGameState.logs.map((l) => l.id)
    seen.mark(currentIds)
  }, [publicGameState.logs, seen])

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    isAtBottomRef.current = distanceFromBottom < 50
  }

  return (
    <div
      className="flex shrink-0 flex-col overflow-hidden border-l border-neutral-300"
      style={{ width: "clamp(485px, calc(100vw - 795px), 600px)" }}
    >
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex min-h-0 grow flex-col gap-0 overflow-y-auto px-4 py-4"
      >
        <div className="flex-1" />
        {publicGameState.logs
          .sort((a, b) => a.id - b.id)
          .map((log: Log) => {
            const isNew =
              seen.initialIds !== null && !seen.initialIds.has(log.id)
            const isUnacknowledged =
              acknowledged.initialIds !== null &&
              !acknowledged.initialIds.has(log.id) &&
              !acknowledged.sessionMarked.has(log.id)
            return (
              <div
                key={log.id}
                className={`relative -mx-4 flex flex-col items-baseline gap-x-4 px-10 py-2 ${isNew ? "animate-log-slide-in" : ""}`}
              >
                {isUnacknowledged && (
                  <div
                    onMouseEnter={() => acknowledged.mark([log.id])}
                    className="absolute left-1 top-1/2 flex h-10 w-10 -translate-y-1/2 items-center justify-center"
                  >
                    <div className="h-2 w-2 rounded-full bg-blue-500" />
                  </div>
                )}
                <div className="flex w-full justify-between gap-x-4 text-sm text-neutral-500">
                  <div className="flex gap-x-2">
                    <div className="whitespace-nowrap">Turn {log.turn}</div>
                    <div className="whitespace-nowrap capitalize">
                      {log.phase} phase
                    </div>
                  </div>
                  <div className="whitespace-nowrap">
                    {formatElapsedDate(log.createdOn, timezone)}
                  </div>
                </div>
                <div className="w-full">{log.text}</div>
              </div>
            )
          })}
      </div>
    </div>
  )
}

export default LogList
