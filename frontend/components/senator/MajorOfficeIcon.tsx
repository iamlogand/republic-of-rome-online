import Image from 'next/image';
import MajorOffice from "../../types/MajorOffice";
import RomeConsulIcon from "../../images/icons/romeConsul.min.svg";
import FieldConsulIcon from "../../images/icons/fieldConsul.min.svg";
import CensorIcon from "../../images/icons/censor.min.svg";
import styles from "./SenatorPortrait.module.css";

interface MajorOfficeIconProps {
  majorOffice: MajorOffice;
  size: number;
}

const MajorOfficeIcon = (props: MajorOfficeIconProps) => {
  if (props.majorOffice === "rome consul") {
    return <Image className={styles.majorOfficeIcon} src={RomeConsulIcon} height={props.size} width={props.size} alt="Rome Consul" />
  } else if (props.majorOffice === "field consul") {
    return <Image className={styles.majorOfficeIcon} src={FieldConsulIcon} height={props.size} width={props.size} alt="Field Consul" />
  } else if (props.majorOffice === "censor") {
    return <Image className={styles.majorOfficeIcon} src={CensorIcon} height={props.size} width={props.size} alt="Censor" />
  } else {
    return null;
  }
}

export default MajorOfficeIcon;
