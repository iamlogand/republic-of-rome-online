import Link from "next/link"

export interface BreadcrumbItem {
  text: string
  href?: string
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
}

const Breadcrumbs = ({ items }: BreadcrumbsProps) => {
  return (
    <div>
      {items.map((item: BreadcrumbItem, index: number) => (
        <span key={index} className="text-neutral-600">
          {item.href ? (
            <span className="text-blue-600 hover:underline">
              <Link href={item.href}>{item.text}</Link>
            </span>
          ) : (
            <span>{item.text}</span>
          )}
          {index < items.length - 1 && <span className="px-3">&#62;</span>}
        </span>
      ))}
    </div>
  )
}

export default Breadcrumbs
