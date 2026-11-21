"use client"

import { useEffect, useMemo, useRef, useState } from "react"

import Log from "@/classes/Log"
import { formatElapsedDate } from "@/helpers/date"
import useLocalStorage from "@/hooks/useLocalStorage"

const INITIAL_LOG_THRESHOLD = 1

interface Props {
  logs: Log[]
  storageKey: string
}

const LogList = ({ logs, storageKey }: Props) => {
  const [timezone, setTimezone] = useState<string>("")
  const scrollRef = useRef<HTMLDivElement>(null)
  const isAtBottomRef = useRef(true)
  const { value: seenLogIds, set: setSeenLogIds } = useLocalStorage<number[]>(
    `${storageKey}-seenLogs`,
  )
  const { value: doneLogIds, set: setDoneLogIds } = useLocalStorage<number[]>(
    `${storageKey}-doneLogs`,
  )

  const [animatingIds, setAnimatingIds] = useState<Set<number>>(() => new Set())
  const doneLogIdSet = useMemo(() => new Set(doneLogIds), [doneLogIds])

  const seenLogIdsRef = useRef(seenLogIds)
  seenLogIdsRef.current = seenLogIds

  const doneLogIdsRef = useRef(doneLogIds)
  doneLogIdsRef.current = doneLogIds

  useEffect(() => {
    setTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone)
  }, [setTimezone])

  // Force re-render every 5 seconds to keep elapsed times fresh
  const [, setRefreshKey] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => setRefreshKey((k) => k + 1), 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (!logs || logs.length < 1) return

    const currentSeen = seenLogIdsRef.current
    const currentDone = doneLogIdsRef.current

    // Initialize doneLogIds if not yet set
    if (currentDone === null) {
      setDoneLogIds([])
    }

    // Populate seen/done on first visit
    const isFirstVisit = !currentSeen || currentSeen.length === 0
    if (isFirstVisit && logs.length > INITIAL_LOG_THRESHOLD) {
      setSeenLogIds(logs.map((log) => log.id))
      setDoneLogIds(logs.map((log) => log.id))
      return
    }

    const seen = new Set(currentSeen)
    const unseenLogs = logs.filter((log) => !seen.has(log.id))

    if (unseenLogs.length === 0) return

    // Apply animation to new logs
    setAnimatingIds((current) => {
      const next = new Set(current)

      unseenLogs.forEach((log) => {
        next.add(log.id)
      })

      return next
    })

    // Scroll to bottom when logs change, only if user hasn't scrolled up
    const el = scrollRef.current
    if (el && isAtBottomRef.current) {
      el.scrollTop = el.scrollHeight
    }

    setSeenLogIds([...(currentSeen ?? []), ...unseenLogs.map((log) => log.id)])
  }, [logs])

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    isAtBottomRef.current = distanceFromBottom < 50
  }

  const handleAnimationEnd = (id: number) => {
    setAnimatingIds((current) => {
      const next = new Set(current)
      next.delete(id)
      return next
    })
  }

  const handleDone = (id: number) => {
    setDoneLogIds([...(doneLogIds ?? []), id])
  }

  return (
    <div
      className="flex h-full shrink-0 flex-col overflow-hidden"
      style={{ width: "clamp(485px, calc(100vw - 795px), 600px)" }}
    >
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex min-h-0 grow flex-col gap-0 overflow-y-auto py-6"
      >
        <div className="flex-1" />
        {[...logs]
          .sort((a, b) => a.id - b.id)
          .map((log: Log) => {
            return (
              <div
                key={log.id}
                className={`flex w-full flex-col py-2 ${animatingIds.has(log.id) ? "animate-highlight" : ""}`}
                onAnimationEnd={() => handleAnimationEnd(log.id)}
              >
                <div className="flex w-full justify-between gap-x-4 px-10 text-sm text-neutral-500">
                  <div className="flex gap-x-2">
                    <div className="whitespace-nowrap">Turn {log.turn}</div>
                    <div className="whitespace-nowrap capitalize">
                      {log.phase} phase
                    </div>
                  </div>
                  <div className="whitespace-nowrap">
                    {timezone && formatElapsedDate(log.createdOn, timezone)}
                  </div>
                </div>
                <div className="flex w-full pr-10">
                  <div
                    className="flex h-6 min-w-10 items-center justify-center"
                    onMouseEnter={() => handleDone(log.id)}
                  >
                    {doneLogIds !== null && !doneLogIdSet.has(log.id) && (
                      <div className="h-2.5 w-2.5 rounded-full bg-blue-500"></div>
                    )}
                  </div>
                  <div className="w-full">{log.text}</div>
                </div>
              </div>
            )
          })}
      </div>
    </div>
  )
}

export default LogList
