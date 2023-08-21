interface PageErrorProps {
  statusCode: number
}

// This component is designed to replace the entire `<main>` element of a page with an error message
const PageError = (props: PageErrorProps) => {

  let message = '';
  switch (props.statusCode) {
    case (404):
      message = "Not found";
      break;
    case (401):
      message = "Unauthorized";
      break;
  }

  return (
    <main className="standard-page">
      <p style={{ textAlign: 'center' }}>Error {props.statusCode} - {message}</p>
    </main>
  )
}

export default PageError;
