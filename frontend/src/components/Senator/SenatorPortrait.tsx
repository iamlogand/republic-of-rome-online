import { useRef, useState } from 'react';
import chroma from "chroma-js"
import "./SenatorPortrait.css";

import FactionLeaderPattern from "../../images/patterns/factionLeader.min.svg";
import Senator from '../../objects/Senator';
import MajorOfficeIcon from './MajorOfficeIcon';

import Cornelius from "../../images/portraits/cornelius.72.png";
import Fabius from "../../images/portraits/fabius.72.png";
import Valerius from "../../images/portraits/valerius.72.png";
import Julius from "../../images/portraits/julius.72.png";

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
    // Get base background color
    let bgColor = props.senator.getColor("bg");

    // Manipulate color to make gradient background
    if (mouseHover === true) {
      bgColor = chroma(bgColor).brighten(1).hex();
    }
    let innerBgColor = chroma(bgColor).brighten().hex();
    let outerBgColor = chroma(bgColor).darken().hex();
    
    // Return background and border styles
    return {
      background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")",
      border: "2px solid " + props.senator.getColor("primary")
    };
  }

  const getPictureClass = () => {
    let cssClass = "picture";
    if (!props.senator.alive) {
      cssClass = cssClass + " grayscale-img"
    }
    return cssClass;
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
    <DynamicTag onMouseEnter={mouseEnter} onMouseLeave={mouseLeave} className="senator-portrait">
      <figure ref={portraitRef}>
        <div style={getStyle()}>
          <img className={getPictureClass()} src={getPicture()} alt={"Portrait of " + props.senator.name} />
          {props.senator.factionLeader && <img className='faction-leader' src={FactionLeaderPattern} alt="Faction Leader" width="70"/>}
          <MajorOfficeIcon majorOffice={props.senator.majorOffice}/>
        </div>
      </figure>
    </DynamicTag>
  )
}

export default SenatorPortrait;
