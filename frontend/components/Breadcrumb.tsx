import Link from "next/link"

export interface BreadcrumbItem {
  text: string
  href?: string
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

const Breadcrumb = ({ items }: BreadcrumbProps) => {
  // If an item has no text, don't render that item or any subsequent items
  // This prevents the breadcrumb from flickering when waiting for data to load
  const emptyItemIndex = items.map((i) => i.text).indexOf("")
  if (emptyItemIndex !== -1) {
    items = items.slice(0, emptyItemIndex)
    items.push({ text: "" })
  }

  return (
    <div className="flex flex-wrap">
      {items.map((item: BreadcrumbItem, index: number) => (
        <div key={index} className="flex text-neutral-600">
          {item.href ? (
            <div className="max-w-[400px] overflow-hidden text-ellipsis whitespace-nowrap text-blue-600 hover:underline">
              <Link href={item.href}>{item.text}</Link>
            </div>
          ) : (
            <div>{item.text}</div>
          )}
          {index < items.length - 1 && <div className="px-3">&#62;</div>}
        </div>
      ))}
    </div>
  )
}

export default Breadcrumb
