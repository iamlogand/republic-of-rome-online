import { useAuthContext } from "@/contexts/AuthContext"

interface PageErrorProps {
  statusCode: number
}

// This component is designed to replace the entire `<main>` element of a page with an error message
const PageError = (props: PageErrorProps) => {
  const { user } = useAuthContext()

  let message = ''
  switch (props.statusCode) {
    case (404):
      message = "Not found"
      break
    case (401):
      message = "Unauthorized"
      break
  }

  const getSuggestion = () => {
    if (props.statusCode === 401 && user === null) return <p><b>Please sign in to access this page</b></p>
  }

  return (
    <main className="standard-page" style={{ textAlign: 'center' }}>
      <p>Error {props.statusCode} - {message}</p>
      {getSuggestion()}
    </main>
  )
}

export default PageError
