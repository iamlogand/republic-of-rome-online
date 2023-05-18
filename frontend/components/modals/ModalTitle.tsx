import { MouseEventHandler } from "react";
import styles from "./ModalTitle.module.css"

interface ModalTitleProps {
  title: string;
  closeAction: MouseEventHandler<HTMLElement>;
  ariaLabel: string;
}

const ModalTitle = (props: ModalTitleProps) => {
  return (
    <div className={styles.modalTitle}>
      <button onClick={props.closeAction} aria-label={props.ariaLabel ?? "Close"}>✖</button>
      <h2 style={{ fontSize: "28px" }}>{props.title}</h2>
    </div>
    )
}

export default ModalTitle;
