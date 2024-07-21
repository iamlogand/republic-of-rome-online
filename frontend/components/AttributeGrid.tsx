import { Tooltip } from "@mui/material"
import Image from "next/image"
import TermLink from "@/components/TermLink"

export interface Attribute {
  name: string
  value: number
  icon: string
  fontSize?: number
  tooltipTitle?: string
  termLinkName?: string
}

interface AttributeGridProps {
  attributes: Attribute[]
}

// A grid of attributes
const AttributeGrid = ({ attributes }: AttributeGridProps) => {
  // Get JSX for an attribute item
  const getAttributeItem = (item: Attribute, index: number) => {
    return (
      <Tooltip key={index} title={item.tooltipTitle} arrow>
        <div
          key={index}
          className={`w-[150px] grid grid-cols-[35px_85px_30px] items-center justify-items-center gap-1`}
        >
          <Image
            src={item.icon}
            height={34}
            width={34}
            alt={`${item.name} icon`}
            style={{ userSelect: "none" }}
          />
          <div className="text-center" style={{ fontSize: item.fontSize }}>
            <TermLink
              name={item.termLinkName ?? item.name}
              displayName={item.name}
              hiddenUnderline
            />
          </div>
          <div className="text-lg font-semibold">{item.value}</div>
        </div>
      </Tooltip>
    )
  }

  if (!attributes) return null

  return (
    <div
      className={`grid grid-cols-[repeat(auto-fill,minmax(150px,1fr))] gap-4 justify-items-center content-start box-border`}
    >
      {attributes.map((attribute: Attribute, index) =>
        getAttributeItem(attribute, index)
      )}
    </div>
  )
}

export default AttributeGrid
