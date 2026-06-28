"use client"

import { ReactNode, useState } from "react"

import {
  FloatingPortal,
  autoUpdate,
  flip,
  offset,
  safePolygon,
  shift,
  useFloating,
  useHover,
  useInteractions,
} from "@floating-ui/react"

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
}: Props) => {
  const [isOpen, setIsOpen] = useState(false)

  const { refs, floatingStyles, context } = useFloating({
    open: isOpen,
    onOpenChange: setIsOpen,
    placement: align === "right" ? "bottom-end" : "bottom-start",
    middleware: [offset(4), flip(), shift({ padding: 8 })],
    whileElementsMounted: autoUpdate,
  })

  const hover = useHover(context, { handleClose: safePolygon() })
  const { getReferenceProps, getFloatingProps } = useInteractions([hover])

  return (
    <div className={className}>
      <div
        ref={refs.setReference}
        className={`cursor-default ${isOpen ? "bg-neutral-100" : ""} ${triggerClassName ?? ""}`}
        {...getReferenceProps()}
      >
        {trigger}
      </div>
      {isOpen && (
        <FloatingPortal>
          <div
            ref={refs.setFloating}
            style={floatingStyles}
            className="z-50"
            {...getFloatingProps()}
          >
            <div className="w-max rounded border border-neutral-300 bg-white p-4 shadow-lg">
              {children}
            </div>
          </div>
        </FloatingPortal>
      )}
    </div>
  )
}

export default Popover
