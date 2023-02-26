import { useRef, useState } from 'react';
import chroma from "chroma-js"
import "./SenatorPortrait.css";
import Cornelius from "../../images/portraits/Cornelius.72.png";
import Fabius from "../../images/portraits/Fabius.72.png";
import Valerius from "../../images/portraits/Valerius.72.png";
import FactionLeaderPattern from "../../images/patterns/FactionLeader.min.svg";
import Senator from '../../objects/Senator';
import MajorOfficeIcon from './MajorOfficeIcon';

interface SenatorPortraitProps {
  senator: Senator;
  setSummaryRef: Function;
}

/**
 * The `SenatorPortrait` contains a picture of the senator it represents.
 * Icons, colors and patterns are used to express basic information about the senator.
 */
const SenatorPortrait = (props: SenatorPortraitProps) => {
  
  const portraitRef = useRef<HTMLDivElement>(null);

  const [mouseHover, setMouseHover] = useState<boolean>(false);
  const [summaryTimer, setSummaryTimer] = useState<any>(null);

  const mouseEnter = () => {
    setMouseHover(true)

    clearTimeout(summaryTimer);
    setSummaryTimer(setTimeout(() => {
      const portraitPosition = portraitRef.current?.getBoundingClientRect();
      if (portraitPosition) {
        props.setSummaryRef({
          parentXOffset: Math.round(portraitPosition.x) + 2,
          parentYOffset: Math.round(portraitPosition.y),
          parentWidth: 76,
          instance: props.senator
        });
      };
    }, 500));
  }

  const mouseLeave = () => {
    clearTimeout(summaryTimer);
    setMouseHover(false);
    setSummaryTimer(null);
    props.setSummaryRef(null);
  }

  const getStyle = () => {
    let style = {};

    // Get base background color
    let bgColor = props.senator.getColor("bg");

    // Manipulate color to make gradient background
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
    
    // Get border color
    const borderColor = props.senator.getColor("primary")
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

  return (
    <figure ref={portraitRef} className="senator-portrait">
      <a href='#' className='link' style={getStyle()} onMouseEnter={mouseEnter} onMouseLeave={mouseLeave}>
        <img className={getPictureClass()} style={getPictureStyle()} src={getPicture()} alt={"Portrait of " + props.senator.name} />
        {getFactionLeaderPattern()}
        <MajorOfficeIcon majorOffice={props.senator.majorOffice}/>
      </a>
    </figure>
  )
}

export default SenatorPortrait;
