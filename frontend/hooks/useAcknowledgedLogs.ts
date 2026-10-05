import { useCallback, useEffect, useRef, useState } from "react"

import {
  deleteTrackedEntry,
  persistTrackedIds,
  readTrackedIds,
} from "./trackedLogsStorage"

const INDEX_KEY = "acknowledged-logs-index"
const storageKey = (gameId: number) => `acknowledged-logs-${gameId}`

const useAcknowledgedLogs = (
  gameId: number | undefined,
  gameFinished: boolean,
) => {
  // Frozen snapshot of IDs acknowledged at mount time — used alongside session
  // state to determine which logs still need a blue dot
  const initialAcknowledgedIdsRef = useRef<Set<number> | null>(null)
  // Mutable set for persistence
  const persistentRef = useRef<Set<number> | null>(null)
  // State-backed set so acknowledging a log triggers a re-render to remove the dot
  const [sessionAcknowledged, setSessionAcknowledged] = useState<Set<number>>(
    new Set(),
  )

  if (persistentRef.current === null && gameId !== undefined) {
    const stored = readTrackedIds(storageKey(gameId))
    persistentRef.current = stored ?? new Set()
    initialAcknowledgedIdsRef.current = stored ? new Set(stored) : null
  }

  useEffect(() => {
    if (gameId !== undefined && gameFinished) {
      deleteTrackedEntry(storageKey(gameId), INDEX_KEY)
    }
  }, [gameId, gameFinished])

  const markAsAcknowledged = useCallback(
    (ids: number[]) => {
      if (!persistentRef.current || gameId === undefined) return
      const newIds = ids.filter((id) => !persistentRef.current!.has(id))
      if (newIds.length === 0) return
      newIds.forEach((id) => persistentRef.current!.add(id))
      persistTrackedIds(storageKey(gameId), INDEX_KEY, persistentRef.current)
      setSessionAcknowledged((prev) => new Set([...prev, ...newIds]))
    },
    [gameId],
  )

  return {
    initialAcknowledgedIds: initialAcknowledgedIdsRef.current,
    sessionAcknowledged,
    markAsAcknowledged,
  }
}

export default useAcknowledgedLogs
