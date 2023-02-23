import MajorOffice from "../../types/MajorOffice";

import RomeConsulIcon from "../../images/icons/RomeConsul.min.svg";
import FieldConsulIcon from "../../images/icons/FieldConsul.min.svg";
import CensorIcon from "../../images/icons/Censor.min.svg";

interface MajorOfficeIconProps {
  majorOffice: MajorOffice;
}

const MajorOfficeIcon = (props: MajorOfficeIconProps) => {
  if (props.majorOffice === "rome consul") {
    return <img className='major-office-icon' src={RomeConsulIcon} alt="Rome Consul" />
  } else if (props.majorOffice === "field consul") {
    return <img className='major-office-icon' src={FieldConsulIcon} alt="Field Consul" />
  } else if (props.majorOffice === "censor") {
    return <img className='major-office-icon' src={CensorIcon} alt="Censor" />
  } else {
    return null;
  }
}

export default MajorOfficeIcon;
