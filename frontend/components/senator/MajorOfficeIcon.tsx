import Image from 'next/image';
import MajorOffice from "../../types/MajorOffice";
import RomeConsulIcon from "../../images/icons/romeConsul.min.svg";
import FieldConsulIcon from "../../images/icons/fieldConsul.min.svg";
import CensorIcon from "../../images/icons/censor.min.svg";
import styles from "./SenatorPortrait.module.css";

interface MajorOfficeIconProps {
  majorOffice: MajorOffice;
}

const MajorOfficeIcon = (props: MajorOfficeIconProps) => {
  if (props.majorOffice === "rome consul") {
    return <Image className={styles.majorOfficeIcon} src={RomeConsulIcon} alt="Rome Consul" />
  } else if (props.majorOffice === "field consul") {
    return <Image className={styles.majorOfficeIcon} src={FieldConsulIcon} alt="Field Consul" />
  } else if (props.majorOffice === "censor") {
    return <Image className={styles.majorOfficeIcon} src={CensorIcon} alt="Censor" />
  } else {
    return null;
  }
}

export default MajorOfficeIcon;
