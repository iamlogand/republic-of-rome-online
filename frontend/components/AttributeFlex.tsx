import Image from "next/image"
import { Tooltip } from "@mui/material"
import { capitalize } from "@mui/material/utils"
import { useCookieContext } from "@/contexts/CookieContext"

export interface Attribute {
  name: string
  value: number
  icon: string
  onClick?: () => void
}

interface AttributeGridProps {
  attributes: Attribute[]
}

const getAttributeItem = (item: Attribute, darkMode: boolean, index?: number) => {

  const titleCaseName = capitalize(item.name)
  return (
    <Tooltip key={index} title={titleCaseName} arrow>
      <div
        className="w-[64px] grid grid-cols-[30px_30px] items-center justify-center rounded"
        style={
          darkMode
            ? {
                // Mostly transparent black
                backgroundColor: "hsla(0, 0%, 0%, 0.25)",
                boxShadow: "0 0 2px 2px hsla(0, 0%, 0%, 0.25)",
              }
            : {
                // Slightly transparent white
                backgroundColor: "hsla(0, 0%, 100%, 0.85)",
                boxShadow: "0 0 2px 2px hsla(0, 0%, 100%, 0.85)",
              }
        }
      >
        <Image
          src={item.icon}
          height={28}
          width={28}
          alt={`${titleCaseName} icon`}
        />
        <div className="w-8 text-center text-md font-semibold">
          {item.value.toString()}
        </div>
      </div>
    </Tooltip>
  )
}

const AttributeFlex = ({ attributes }: AttributeGridProps) => {
  const { darkMode } = useCookieContext()

  const getButton = (item: Attribute, index: number) => {
    if (item.onClick === undefined) return getAttributeItem(item, darkMode, index)
    return (
      <button
        key={index}
        onClick={item.onClick}
        className="cursor-pointer border-0 p-0 bg-transparent"
      >
        {getAttributeItem(item, darkMode)}
      </button>
    )
  }

  return (
    <div className="p-[2px] flex flex-wrap gap-3 select-none">
      {attributes.map((attribute: Attribute, index) =>
        getButton(attribute, index)
      )}
    </div>
  )
}

export default AttributeFlex
