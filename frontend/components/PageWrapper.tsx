import { ReactNode, useEffect, useState } from "react"
import Cookies from "js-cookie"
import { useCookieContext } from "@/contexts/CookieContext"

interface PageWrapperProps {
  children: ReactNode
  reference: any
}

// Wraps the top bar, page content and footer
const PageWrapper = (props: PageWrapperProps) => {
  const { darkMode } = useCookieContext()
  const [isReady, setIsReady] = useState(false)

  // Set the timezone cookie
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
  Cookies.set("timezone", timezone)

  useEffect(() => {
    if (darkMode !== undefined) {
      setIsReady(true)
      if (darkMode) {
        document.body.classList.add("dark")
      } else {
        document.body.classList.remove("dark")
      }
    }
  }, [darkMode])

  // This prevents a hydration issue where the page content is rendered before the darkMode cookie is read
  if (!isReady) {
    return null
  }

  return (
    <div ref={props.reference} className="non-modal-content">
      {props.children}
    </div>
  )
}

export default PageWrapper
