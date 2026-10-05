import { useCallback, useEffect, useRef } from "react"

import {
  deleteTrackedEntry,
  persistTrackedIds,
  readTrackedIds,
} from "./trackedLogsStorage"

const INDEX_KEY = "seen-logs-index"
const storageKey = (gameId: number) => `seen-logs-${gameId}`

const useSeenLogs = (gameId: number | undefined, gameFinished: boolean) => {
  // Frozen snapshot of IDs seen at mount time — never mutated, used for isNew checks
  const initialSeenIdsRef = useRef<Set<number> | null>(null)
  // Mutable set used only for persistence — not for rendering decisions
  const seenIdsRef = useRef<Set<number> | null>(null)

  if (seenIdsRef.current === null && gameId !== undefined) {
    const stored = readTrackedIds(storageKey(gameId))
    seenIdsRef.current = stored ?? new Set()
    initialSeenIdsRef.current = stored ? new Set(stored) : null
  }

  useEffect(() => {
    if (gameId !== undefined && gameFinished) {
      deleteTrackedEntry(storageKey(gameId), INDEX_KEY)
    }
  }, [gameId, gameFinished])

  const markAsSeen = useCallback(
    (ids: number[]) => {
      if (!seenIdsRef.current || gameId === undefined) return
      const newIds = ids.filter((id) => !seenIdsRef.current!.has(id))
      if (newIds.length === 0) return
      newIds.forEach((id) => seenIdsRef.current!.add(id))
      persistTrackedIds(storageKey(gameId), INDEX_KEY, seenIdsRef.current)
    },
    [gameId],
  )

  return {
    initialSeenIds: initialSeenIdsRef.current,
    markAsSeen,
  }
}

export default useSeenLogs
