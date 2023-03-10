import { useRef, useState } from 'react';
import chroma from "chroma-js"
import "./SenatorPortrait.css";

import FactionLeaderPattern from "../../images/patterns/FactionLeader.min.svg";
import Senator from '../../objects/Senator';
import MajorOfficeIcon from './MajorOfficeIcon';

import Cornelius from "../../images/portraits/Cornelius.72.png";
import Fabius from "../../images/portraits/Fabius.72.png";
import Valerius from "../../images/portraits/Valerius.72.png";
import Julius from "../../images/portraits/Julius.72.png";

interface SenatorPortraitProps {
  senator: Senator;
  setInspectorRef: Function | null;
}

/**
 * The `SenatorPortrait` contains a picture of the senator it represents.
 * Icons, colors and patterns are used to express basic information about the senator.
 * 
 * Portraits linked to a inspector (see `props.setInspectorRef`) can be considered "active"
 * and portraits not linked to a inspector can be considered "inactive".
 */
const SenatorPortrait = (props: SenatorPortraitProps) => {
  
  const portraitRef = useRef<HTMLDivElement>(null);

  const [mouseHover, setMouseHover] = useState<boolean>(false);
  const [inspectorTimer, setInspectorTimer] = useState<any>(null);

  const mouseEnter = () => {
    // Only react to this trigger if the portrait is linked to a inspector
    if (props.setInspectorRef !== null) {
      setMouseHover(true)
      clearTimeout(inspectorTimer);
      setInspectorTimer(setTimeout(() => {
        const selfPosition = portraitRef.current?.getBoundingClientRect();
        if (selfPosition && props.setInspectorRef !== null) {
          props.setInspectorRef({
            XOffset: Math.round(selfPosition.x + 2),
            YOffset: Math.round(selfPosition.y),
            width: Math.round(selfPosition.width - 4),
            instance: props.senator
          });
        };
      }, 500));
    }
  }

  const mouseLeave = () => {
    if (props.setInspectorRef !== null) {
      clearTimeout(inspectorTimer);
      setMouseHover(false);
      setInspectorTimer(null);
      props.setInspectorRef(null);
    }
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

  /**
   * Get the correct picture based on the senators name.
   * This will get very long when more senators are included, so this logic should be moved to a helper method.
   */ 
  const getPicture = () => {
    if (props.senator.name === "cornelius") {
      return Cornelius
    } else if (props.senator.name === "fabius") {
      return Fabius
    } else if (props.senator.name === "valerius") {
      return Valerius
    } else if (props.senator.name === "julius") {
      return Julius
    }
  }

  // For semantic reasons, use the `a` tag only if the portrait is linked to a senator inspector
  const DynamicTag = props.setInspectorRef ? "a" : "div";

  return (
    <figure ref={portraitRef} className="senator">
      <DynamicTag href='#' style={getStyle()} onMouseEnter={mouseEnter} onMouseLeave={mouseLeave}>
        <img className={getPictureClass()} style={getPictureStyle()} src={getPicture()} alt={"Portrait of " + props.senator.name} />
        {props.senator.factionLeader && <img className='faction-leader' src={FactionLeaderPattern} alt="Faction Leader" width="70"/>}
        <MajorOfficeIcon majorOffice={props.senator.majorOffice}/>
      </DynamicTag>
    </figure>
  )
}

export default SenatorPortrait;
