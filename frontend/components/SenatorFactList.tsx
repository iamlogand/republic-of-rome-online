import { useLayoutEffect, useMemo, useRef, useState } from "react"
import Senator from "@/classes/Senator"
import { useGameContext } from "@/contexts/GameContext"
import SenatorFact from "@/components/SenatorFact"
import HiddenSenatorFacts from "@/components/HiddenSenatorFacts"

const TITLE_DISPLAY_ORDER = [
  "HRAO",
  "Dictator",
  "Temporary Rome Consul",
  "Rome Consul",
  "Field Consul",
  "Censor",
  "Master of Horse",
  "Prior Consul",
]

export type SenatorFactListItem = {
  name: string
  termName?: string
  customSeparator?: JSX.Element // Custom separator to follow the item instead of the default ", " or " and "
}

interface SenatorFactListProps {
  senator: Senator
  selectable?: boolean
}

// A series of facts about a given senator
const SenatorFactList = ({ senator, selectable }: SenatorFactListProps) => {
  const { allTitles, allConcessions } = useGameContext()
  const [compressedItemCount, setCompressedItemCount] = useState<number>(0)
  const [hiddenItemCount, setHiddenItemCount] = useState<number>(0)
  const containerRef = useRef<HTMLDivElement>(null)

  const items: SenatorFactListItem[] = useMemo(() => {
    // Get the senator's titles
    const titles = allTitles.asArray.filter(
      (t) => t.senator === senator.id && t.name !== "Faction Leader"
    )
    const items: SenatorFactListItem[] = titles.map((t) => {
      return {
        name: t.name,
        termName: t.name,
      }
    })

    // Sort the titles
    items.sort((a, b) => {
      const aIndex = TITLE_DISPLAY_ORDER.indexOf(a.name)
      const bIndex = TITLE_DISPLAY_ORDER.indexOf(b.name)
      if (aIndex === -1 && bIndex === -1) return a.name.localeCompare(b.name)
      else if (aIndex === -1) return 1
      else if (bIndex === -1) return -1
      else return aIndex - bIndex
    })

    // Get the senator's concessions
    const concessions = allConcessions.asArray.filter(
      (c) => c.senator === senator.id
    )
    concessions.forEach((c) => {
      let termName = c.name
      if (c.name.endsWith("Tax Farmer")) termName = "Tax Farmer"
      if (c.name.endsWith("Grain")) termName = "Grain"
      items.push({
        name: c.name,
        termName: termName,
      })
    })

    // Add HRAO
    if (senator.rank !== null && senator.rank <= 0)
      items.unshift({
        name: "HRAO",
        termName: "HRAO",
      })

    // Add Dead Senator or Senator
    if (!senator.alive) {
      items.unshift({
        name: "Dead Senator",
        customSeparator: items.length > 0 ? <span>, was </span> : undefined,
      })
    } else {
      items.push({
        name: "Senator",
        termName: "Senator",
      })
    }

    return items
  }, [senator, allTitles, allConcessions])

  // Increase compressed items then hidden items until there's no more overflow
  useLayoutEffect(() => {
    const container = containerRef.current
    if (container) {
      const resizeObserver = new ResizeObserver(() => {
        if (container.scrollHeight > container.clientHeight) {
          if (compressedItemCount < items.length) {
            setCompressedItemCount((prevCount) => prevCount + 1)
          } else if (hiddenItemCount < items.length) {
            setHiddenItemCount((prevCount) => prevCount + 1)
          }
        }
      })

      resizeObserver.observe(container)

      // Cleanup function to stop observing when component unmounts or re-renders
      return () => {
        resizeObserver.unobserve(container)
      }
    }
  }, [containerRef, items, compressedItemCount, hiddenItemCount])

  if (!senator || items.length === 0) return null

  const renderSeparator = (index: number, isTermLink: boolean) => {
    if (isTermLink && compressedItemCount >= items.length) {
      return "" // No separator needed if all items are compressed
    }
    if (index < items.length - 2) {
      return ", "
    }
    if (index === items.length - 2 && items.length > 1) {
      if (compressedItemCount > 1) {
        return ", "
      } else {
        return " and "
      }
    }
  }

  return (
    <div ref={containerRef}>
      {items.map(
        (item: SenatorFactListItem, index: number) =>
          index < items.length - hiddenItemCount && (
            <span key={index}>
              <SenatorFact
                name={item.name}
                termName={item.termName}
                selectable={selectable}
                compressed={index >= items.length - compressedItemCount}
              />
              {item.customSeparator
                ? item.customSeparator
                : renderSeparator(index, item.termName !== undefined)}
            </span>
          )
      )}
      {hiddenItemCount > 0 && (
        <HiddenSenatorFacts items={items.slice(-hiddenItemCount)} />
      )}
    </div>
  )
}

export default SenatorFactList
