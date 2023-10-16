import Image from "next/image"

export interface Attribute {
  name: string
  value: number
  icon: string
}

interface AttributeGridProps {
  attributes: Attribute[]
}

// A grid of attributes 
const AttributeGrid = ({ attributes }: AttributeGridProps) => {
  
  // Get JSX for an attribute item
  const getAttributeItem = (item: Attribute, index: number) => {
    
    return (
      <div
        key={index}
        className={`w-[150px] grid grid-cols-[85px_35px_30px] items-center justify-items-center`}
      >
        <div className="text-center">{item.name}</div>
        <Image
          src={item.icon}
          height={34}
          width={34}
          alt={`${item.name} icon`}
          style={{ userSelect: "none" }}
        />
        <div>{item.value}</div>
      </div>
    )
  }

  if (!attributes) return null

  return (
    <div className={`grid grid-cols-[repeat(auto-fill,minmax(150px,1fr))] gap-2 justify-items-center`}>
      {attributes.map((attribute: Attribute, index) => getAttributeItem(attribute, index))}
    </div>
  )
}

export default AttributeGrid
