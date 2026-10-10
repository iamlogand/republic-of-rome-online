import { useCallback, useState } from "react"

const useLocalStorage = <T>(key: string) => {
  const [value, setValue] = useState<T | null>(() => {
    if (typeof localStorage === "undefined") return null
    const raw = localStorage.getItem(key)
    if (raw === null) return null
    try {
      return JSON.parse(raw) as T
    } catch {
      return null
    }
  })

  const set = useCallback(
    (next: T) => {
      setValue(next)
      localStorage.setItem(key, JSON.stringify(next))
    },
    [key],
  )

  const remove = useCallback(() => {
    setValue(null)
    localStorage.removeItem(key)
  }, [key])

  return { value, set, remove }
}

export default useLocalStorage
