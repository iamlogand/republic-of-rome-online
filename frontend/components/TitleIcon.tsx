import Image from 'next/image'
import RomeConsulIcon from "@/images/icons/romeConsul.svg"
import styles from "./TitleIcon.module.css"
import Title from "@/classes/Title"

interface TitleIconProps {
  title: Title;
  size: number;
}

const TitleIcon = (props: TitleIconProps) => {
  if (props.title.name.includes("Rome Consul")) {
    return <Image className={styles.titleIcon} src={RomeConsulIcon} height={props.size} width={props.size} alt="Rome Consul icon" />
  } else {
    return null;
  }
}

export default TitleIcon;
