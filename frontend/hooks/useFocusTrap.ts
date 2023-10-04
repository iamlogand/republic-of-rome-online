import { RefObject, useEffect, useLayoutEffect } from "react"

const useFocusTrap = (ref: RefObject<HTMLElement>): void => {
  useLayoutEffect(() => {
    if (ref.current) {
      const firstFocusableElement = ref.current.querySelector(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
      ) as HTMLElement
      if (firstFocusableElement) {
        firstFocusableElement.focus()
      }
    }
  }, [ref])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Tab" && ref.current) {
        const focusableElements = ref.current.querySelectorAll(
          'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
        )
        if (focusableElements.length > 0) {
          const firstElement = focusableElements[0] as HTMLElement
          const lastElement = focusableElements[
            focusableElements.length - 1
          ] as HTMLElement

          if (event.shiftKey && document.activeElement === firstElement) {
            lastElement.focus()
            event.preventDefault()
          } else if (
            !event.shiftKey &&
            document.activeElement === lastElement
          ) {
            firstElement.focus()
            event.preventDefault()
          }
        }
      }
    }

    if (ref.current) {
      document.addEventListener("keydown", handleKeyDown)
    }

    return () => {
      document.removeEventListener("keydown", handleKeyDown)
    }
  }, [ref])
}

export default useFocusTrap
