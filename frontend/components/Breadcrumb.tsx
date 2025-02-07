import Link from "next/link"

export interface BreadcrumbItem {
  text: string
  href?: string
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

const Breadcrumb = ({ items }: BreadcrumbProps) => {
  return (
    <div className="flex">
      {items.map((item: BreadcrumbItem, index: number) => (
        <div key={index} className="text-neutral-600 flex">
          {item.href ? (
            <div className="max-w-[400px] text-ellipsis whitespace-nowrap overflow-hidden text-blue-600 hover:underline">
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
