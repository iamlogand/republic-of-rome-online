import { useDialogContext } from "@/contexts/DialogContext";
import styles from "./DialogBackdrop.module.css"

const DialogBackdrop = () => {
  const { setDialog } = useDialogContext();

  const handleClick = () => {
    setDialog('')
  }

  return (
    <div onClick={handleClick} className={styles.dialogBackdrop}>
    </div>
  )
}

export default DialogBackdrop;
