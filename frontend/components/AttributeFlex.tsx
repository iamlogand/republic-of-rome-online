import Image from "next/image"
import { Tooltip } from "@mui/material"
import { capitalize } from "@mui/material/utils"

export interface Attribute {
  name: string
  value: number
  icon: string
}

interface AttributeGridProps {
  attributes: Attribute[]
}

const AttributeFlex = ({ attributes }: AttributeGridProps) => {
  // Get attribute items
  const getAttributeItem = (item: Attribute, index: number) => {
    const titleCaseName = capitalize(item.name)
    return (
      <Tooltip key={index} title={titleCaseName} enterDelay={500} arrow>
        <div className="w-[64px] grid grid-cols-[30px_30px] items-center justify-center bg-white shadow-[0px_0px_2px_2px_white] rounded">
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

  return (
    <div className="p-[2px] flex flex-wrap gap-3 select-none">
      {attributes.map((attribute: Attribute, index) =>
        getAttributeItem(attribute, index)
      )}
    </div>
  )
}

export default AttributeFlex
