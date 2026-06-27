"use client"

import { ReactNode } from "react"

interface Props {
  trigger: ReactNode
  children: ReactNode
  align?: "left" | "right"
  className?: string
  triggerClassName?: string
}

const Popover = ({
  trigger,
  children,
  align = "left",
  className,
  triggerClassName,
}: Props) => (
  <div className={`group relative ${className ?? ""}`}>
    <div
      className={`cursor-default group-hover:bg-neutral-100 ${triggerClassName}`}
    >
      {trigger}
    </div>
    <div
      className={`absolute top-full z-50 hidden pt-1 group-hover:block ${
        align === "right" ? "right-0" : "left-0"
      }`}
    >
      <div className="w-max rounded border border-neutral-300 bg-white p-4 shadow-lg">
        {children}
      </div>
    </div>
  </div>
)

export default Popover
