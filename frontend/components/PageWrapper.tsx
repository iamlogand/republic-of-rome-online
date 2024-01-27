import { ReactNode, useEffect, useState } from "react"
import Cookies from "js-cookie"
import { useAuthContext } from "@/contexts/AuthContext"

interface PageWrapperProps {
  children: ReactNode
  reference: any
}

// Wraps the top bar, page content and footer
const PageWrapper = (props: PageWrapperProps) => {
  const { darkMode } = useAuthContext()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    if (!Cookies.get("timezone")) {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      Cookies.set("timezone", timezone)
    }
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
