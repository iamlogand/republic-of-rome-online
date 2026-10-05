const MAX_ENTRIES = 100

const readIndex = (indexKey: string): string[] => {
  if (typeof localStorage === "undefined") return []
  try {
    return JSON.parse(localStorage.getItem(indexKey) ?? "[]")
  } catch {
    return []
  }
}

export const readTrackedIds = (key: string): Set<number> | null => {
  if (typeof localStorage === "undefined") return null
  const raw = localStorage.getItem(key)
  if (raw === null) return null
  try {
    return new Set(JSON.parse(raw) as number[])
  } catch {
    return null
  }
}

export const persistTrackedIds = (
  key: string,
  indexKey: string,
  ids: Set<number>,
): void => {
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

export const deleteTrackedEntry = (key: string, indexKey: string): void => {
  if (typeof localStorage === "undefined") return
  localStorage.removeItem(key)
  const index = readIndex(indexKey).filter((k) => k !== key)
  localStorage.setItem(indexKey, JSON.stringify(index))
}
