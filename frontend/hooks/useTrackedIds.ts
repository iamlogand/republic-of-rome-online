import { useCallback, useEffect, useRef, useState } from "react"

const MAX_ENTRIES = 100

const readIndex = (indexKey: string): string[] => {
  if (typeof localStorage === "undefined") return []
  try {
    return JSON.parse(localStorage.getItem(indexKey) ?? "[]")
  } catch {
    return []
  }
}

const readIds = (key: string): Set<number> | null => {
  if (typeof localStorage === "undefined") return null
  const raw = localStorage.getItem(key)
  if (raw === null) return null
  try {
    return new Set(JSON.parse(raw) as number[])
  } catch {
    return null
  }
}

const persistIds = (key: string, indexKey: string, ids: Set<number>) => {
  if (typeof localStorage === "undefined") return
  localStorage.setItem(key, JSON.stringify(Array.from(ids)))

  const index = readIndex(indexKey).filter((k) => k !== key)
  index.push(key)

  if (index.length > MAX_ENTRIES) {
    const evicted = index.shift()!
    localStorage.removeItem(evicted)
  }

  localStorage.setItem(indexKey, JSON.stringify(index))
}

const deleteEntry = (key: string, indexKey: string) => {
  if (typeof localStorage === "undefined") return
  localStorage.removeItem(key)
  const index = readIndex(indexKey).filter((k) => k !== key)
  localStorage.setItem(indexKey, JSON.stringify(index))
}

const useTrackedIds = (
  prefix: string,
  scopeId: number | string | undefined,
  deleteOnCleanup: boolean,
) => {
  const storageKey = `${prefix}-${scopeId}`
  const indexKey = `${prefix}-index`

  // Frozen snapshot from mount time - never mutated
  const initialIdsRef = useRef<Set<number> | null>(null)
  // Mutable set for persistence only
  const persistentRef = useRef<Set<number> | null>(null)
  // State-backed set of IDs marked during this session, triggers re-renders
  const [sessionMarked, setSessionMarked] = useState<Set<number>>(new Set())

  if (persistentRef.current === null && scopeId !== undefined) {
    const stored = readIds(storageKey)
    persistentRef.current = stored ?? new Set()
    initialIdsRef.current = stored ? new Set(stored) : null
  }

  useEffect(() => {
    if (scopeId !== undefined && deleteOnCleanup) {
      deleteEntry(storageKey, indexKey)
    }
  }, [scopeId, deleteOnCleanup, storageKey, indexKey])

  const mark = useCallback(
    (ids: number[]) => {
      if (!persistentRef.current || scopeId === undefined) return
      const newIds = ids.filter((id) => !persistentRef.current!.has(id))
      if (newIds.length === 0) return
      newIds.forEach((id) => persistentRef.current!.add(id))
      persistIds(storageKey, indexKey, persistentRef.current)
      setSessionMarked((prev) => new Set([...prev, ...newIds]))
    },
    [scopeId, storageKey, indexKey],
  )

  return {
    initialIds: initialIdsRef.current,
    sessionMarked,
    mark,
  }
}

export default useTrackedIds
