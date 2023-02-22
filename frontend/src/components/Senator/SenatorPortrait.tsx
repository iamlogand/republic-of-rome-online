import { useRef, useState } from 'react';
import chroma from "chroma-js"

import "./SenatorPortrait.css";
import SenatorSummary from "./SenatorSummary";

import Cornelius from "../../images/portraits/Cornelius.72.png";
import Fabius from "../../images/portraits/Fabius.72.png";
import Valerius from "../../images/portraits/Valerius.72.png";

import FactionLeaderPattern from "../../images/patterns/FactionLeader.min.svg";
import RomeConsulIcon from "../../images/icons/RomeConsul.min.svg";
import FieldConsulIcon from "../../images/icons/FieldConsul.min.svg";
import CensorIcon from "../../images/icons/Censor.min.svg";
import Senator from '../../objects/Senator';

interface SenatorPortraitProps {
  senator: Senator;
  borderColor: string;
  bgColor: string;
}

/**
 * The `SenatorPortrait` contains a picture of the senator it represents.
 * Icons, colors and patterns are used to express basic information about the senator.
 */
const SenatorPortrait = (props: SenatorPortraitProps) => {
  
  const portraitRef = useRef<HTMLDivElement>(null);

  const [mouseHover, setMouseHover] = useState<boolean>(false);
  const [summaryVisible, setSummaryVisible] = useState<boolean>(false);
  const [summaryRef, setSummaryRef] = useState<any>(null);
  const [summaryTimer, setSummaryTimer] = useState<any>(null);

  const mouseEnter = () => {
    setMouseHover(true)

    clearTimeout(summaryTimer);
    setSummaryTimer(setTimeout(() => {
      const portraitPosition = portraitRef.current?.getBoundingClientRect();
      if (portraitPosition) {
        setSummaryRef({ parentXOffset: Math.round(portraitPosition.x), parentYOffset: Math.round(portraitPosition.y) });
        setSummaryVisible(true);
      };
    }, 500));
  }

  const mouseLeave = () => {
    clearTimeout(summaryTimer);
    setMouseHover(false);
    setSummaryVisible(false);
    setSummaryTimer(null);
  }

  const getStyle = () => {
    let style = {};

    // Define background style
    let bgColor = !props.senator.alive ? "#717171": props.bgColor;
    if (mouseHover === true) {
      bgColor = chroma(bgColor).brighten(1).hex();
    }
    let innerBgColor = chroma(bgColor).brighten().hex();
    let outerBgColor = chroma(bgColor).darken().hex();
    Object.assign(style, {background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")"});
    return style;
  }

  const getPictureClass = () => {
    let cssClass = "picture";
    if (!props.senator.alive) {
      cssClass = cssClass + " grayscale-img"
    }
    return cssClass;
  }

  const getPictureStyle = () => {
    let style = {};
    const borderColor = !props.senator.alive ? "#444444" : props.borderColor;
    Object.assign(style, {border: "2px solid " + borderColor});
    return style;
  }

  const getPicture = () => {
    if (props.senator.name === "cornelius") {
      return Cornelius
    } else if (props.senator.name === "fabius") {
      return Fabius
    } else if (props.senator.name === "valerius") {
      return Valerius
    }
  }

  const getFactionLeaderPattern = () => {
    if (props.senator.factionLeader === true) {
      return <img className='faction-leader' src={FactionLeaderPattern} alt="Faction Leader" width="70"/>
    }
  }

  const getMajorOfficeIcon = () => {
    if (props.senator.majorOffice === "rome consul") {
      return <img className='major-office' src={RomeConsulIcon} alt="Rome Consul" width="30" height="30" />
    } else if (props.senator.majorOffice === "field consul") {
      return <img className='major-office' src={FieldConsulIcon} alt="Field Consul" width="30" height="30" />
    } else if (props.senator.majorOffice === "censor") {
      return <img className='major-office' src={CensorIcon} alt="Censor" width="30" height="30" />
    }
  }

  const getSenatorSummary = () => {
    if (summaryVisible === true) {
      return <SenatorSummary {...props} {...summaryRef} className={summaryVisible ? 'fade-in' : ''} />
    } 
  }

  return (
    <figure ref={portraitRef} className="senator-portrait">
      <a href='#' className='link' style={getStyle()} onMouseEnter={mouseEnter} onMouseLeave={mouseLeave}>
        <img className={getPictureClass()} style={getPictureStyle()} src={getPicture()} alt={"Portrait of " + props.senator.name} />
        {getFactionLeaderPattern()}
        {getMajorOfficeIcon()}
      </a>
      {getSenatorSummary()}
    </figure>
  )
}

export default SenatorPortrait;
