import chroma from "chroma-js"
import Senator from "@/classes/Senator"
import SenatorPortrait from "./SenatorPortrait"
import { useCookieContext } from "@/contexts/CookieContext"
import {
  Neutral100,
  Neutral500,
  Neutral550,
  Tyrian100,
  Tyrian200,
  Tyrian50,
  Tyrian500,
  Tyrian600,
  Tyrian900,
  Tyrian950,
} from "@/themes/colors"
import { useState } from "react"

interface SenatorSelectorItemProps {
  senator: Senator | null
  selected: boolean
  onSelect: (senator: Senator | null) => void
}

const SenatorSelectorItem = ({
  senator,
  selected,
  onSelect,
}: SenatorSelectorItemProps) => {
  const { darkMode } = useCookieContext()
  const [hover, setHover] = useState(false)

  let backgroundColor = null
  if (selected) {
    if (darkMode) {
      backgroundColor = hover
        ? chroma.mix(Tyrian500, Neutral550, 0.75)
        : chroma.mix(Tyrian600, Neutral550, 0.75)
    } else {
      backgroundColor = hover ? chroma.mix(Tyrian100, Neutral100) : Tyrian50
    }
  } else {
    if (darkMode) {
      backgroundColor = hover ? Neutral550 : null
    } else {
      backgroundColor = hover ? Neutral100 : null
    }
  }
  return (
    <button
      onClick={() => onSelect(senator)}
      className={
        "cursor-pointer bg-transparent text-left px-1 py-0 border-0 w-full w-[240px]"
      }
      style={backgroundColor ? { backgroundColor: backgroundColor } : {}}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      {senator ? (
        <div className="flex items-center gap-4 h-[66px]">
          <SenatorPortrait senator={senator} size={60} summary />
          <span className="font-semibold">{senator.displayName}</span>
        </div>
      ) : (
        <div className="h-[40px] ml-[17px] flex items-center">None</div>
      )}
    </button>
  )
}

export default SenatorSelectorItem
