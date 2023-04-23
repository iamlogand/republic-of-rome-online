const { romanice } = require('romanice');
import styles from "./PageError.module.css"

interface PageErrorProps {
  statusCode: number
}

// This component is designed to replace the entire `<main>` element of a page with an error message
const PageError = (props: PageErrorProps) => {

  let message = '';
  switch (props.statusCode) {
    case (404):
      message = "Pagina Non Inventa";
      break;
    case (401):
      message = "Non Auctorizatus";
      break;
  }

  const stylizedErrorCode = romanice().toRoman(props.statusCode);

  return (
    <main>
      <p className={styles.error}>Error <span className={styles.statusCode}>{stylizedErrorCode}</span> - {message}</p>
    </main>
  )
}

export default PageError;