"use client"

import { ReactNode, useState } from "react"

import {
  FloatingFocusManager,
  FloatingPortal,
  autoUpdate,
  flip,
  offset,
  safePolygon,
  shift,
  useDismiss,
  useFloating,
  useFocus,
  useHover,
  useInteractions,
} from "@floating-ui/react"

interface Props {
  trigger: ReactNode
  children: ReactNode
  className?: string
  triggerClassName?: string
}

const Popover = ({ trigger, children, className, triggerClassName }: Props) => {
  const [isOpen, setIsOpen] = useState(false)

  const { refs, floatingStyles, context } = useFloating({
    open: isOpen,
    onOpenChange: setIsOpen,
    placement: "bottom-start",
    middleware: [offset(4), flip(), shift({ padding: 8 })],
    whileElementsMounted: autoUpdate,
  })

  const hover = useHover(context, {
    delay: { open: 150, close: 0 },
    handleClose: safePolygon(),
  })
  const focus = useFocus(context)
  const dismiss = useDismiss(context)
  const { getReferenceProps, getFloatingProps } = useInteractions([
    hover,
    focus,
    dismiss,
  ])

  return (
    <div className={className}>
      <button
        ref={refs.setReference}
        type="button"
        className={`cursor-default outline-none ${isOpen ? "bg-neutral-100" : ""} ${triggerClassName ?? ""}`}
        {...getReferenceProps()}
      >
        {trigger}
      </button>
      {isOpen && (
        <FloatingPortal>
          <FloatingFocusManager
            context={context}
            modal={false}
            initialFocus={-1}
          >
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
          </FloatingFocusManager>
        </FloatingPortal>
      )}
    </div>
  )
}

export default Popover
