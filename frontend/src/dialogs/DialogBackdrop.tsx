interface DialogBackdropProps {
  setDialog: Function
}

const DialogBackdrop = (props: DialogBackdropProps) => {
  const handleClick = () => {
    props.setDialog('')
  }

  return (
    <div onClick={handleClick} className="dialog-backdrop">
    </div>
  )
}

export default DialogBackdrop;
