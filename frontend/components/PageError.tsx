import { useCookieContext } from "@/contexts/CookieContext"

interface PageErrorProps {
  statusCode: number
}

// This component is designed to replace the entire `<main>` element of a page with an error message
const PageError = (props: PageErrorProps) => {
  const { user } = useCookieContext()

  let message = ""
  switch (props.statusCode) {
    case 404:
      message = "Not found"
      break
    case 401:
      message = "Unauthorized"
      break
  }

  const getSuggestion = () => {
    if (props.statusCode === 401 && user === null)
      return (
        <p className="text-center">
          <b>Please sign in to access this page</b>
        </p>
      )
  }

  return (
    <main className="standard-page flex flex-col p-8 gap-2 items-center">
      <p className="text-center">
        Error {props.statusCode} - {message}
      </p>
      {getSuggestion()}
    </main>
  )
}

export default PageError
