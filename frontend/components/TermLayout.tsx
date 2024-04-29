import { ReactNode } from "react"
import ExternalLink from "@/components/ExternalLink"

interface TermLayoutProps {
  title: string
  icon: ReactNode
  children: ReactNode
  category?: string
  wikipediaPage?: string
}

const TermLayout = ({
  title,
  icon,
  children,
  category,
  wikipediaPage,
}: TermLayoutProps) => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <div className="flex items-start gap-4">
        {icon}
        <div>
          <h5 className="text-sm text-neutral-500 dark:text-neutral-300">
            Game Terminology
          </h5>
          <h4 className="text-lg">
            <b>{title}</b>
            {category && <span> ({category})</span>}
          </h4>
          {wikipediaPage && (
            <p className="pt-0">
              <ExternalLink
                href={`https://en.wikipedia.org/wiki/${wikipediaPage}`}
              >
                Wikipedia
              </ExternalLink>
            </p>
          )}
        </div>
      </div>
      <div className="flex flex-col gap-4">{children}</div>
    </div>
  )
}

export default TermLayout
