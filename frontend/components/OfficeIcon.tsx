import Image from 'next/image'
import RomeConsulIcon from "@/images/icons/romeConsul.min.svg"
import styles from "./OfficeIcon.module.css"
import Office from "@/classes/Office"

interface OfficeIconProps {
  office: Office;
  size: number;
}

const OfficeIcon = (props: OfficeIconProps) => {
  if (props.office.name.includes("Rome Consul")) {
    return <Image className={styles.officeIcon} src={RomeConsulIcon} height={props.size} width={props.size} alt="Rome Consul" />
  } else {
    return null;
  }
}

export default OfficeIcon;
