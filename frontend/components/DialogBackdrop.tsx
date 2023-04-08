import styles from "./DialogBackdrop.module.css"

interface DialogBackdropProps {
  setDialog: Function
}

const DialogBackdrop = (props: DialogBackdropProps) => {
  const handleClick = () => {
    props.setDialog('')
  }

  return (
    <div onClick={handleClick} className={styles.dialogBackdrop}>
    </div>
  )
}

export default DialogBackdrop;
