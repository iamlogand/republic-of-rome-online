import Image from "next/image"
import { Tooltip } from "@mui/material"
import { capitalize } from "@mui/material/utils"

export interface Attribute {
  name: string
  value: number
  icon: string
  onClick?: () => void
}

interface AttributeGridProps {
  attributes: Attribute[]
}

const getAttributeItem = (item: Attribute, index?: number) => {
  const titleCaseName = capitalize(item.name)
  return (
    <Tooltip key={index} title={titleCaseName} enterDelay={500} arrow>
      <div className="w-[64px] grid grid-cols-[30px_30px] items-center justify-center bg-white dark:bg-stone-650 shadow-[0px_0px_2px_2px_white] dark:shadow-stone-650 rounded">
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
  const getButton = (item: Attribute, index: number) => {
    if (item.onClick === undefined) return getAttributeItem(item, index)
    return (
      <button
        key={index}
        onClick={item.onClick}
        className="cursor-pointer border-0 p-0 bg-transparent"
      >
        {getAttributeItem(item)}
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
