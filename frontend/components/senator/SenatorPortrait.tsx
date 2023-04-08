import { useRef, useState } from 'react';
import chroma from "chroma-js";
import Image, { StaticImageData } from 'next/image'
import styles from "./SenatorPortrait.module.css";

import MajorOfficeIcon from './MajorOfficeIcon';
import FactionLeaderPattern from "../../images/patterns/factionLeader.min.svg";
import Senator from '@/classes/Senator';

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
            senator: props.senator
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

  const getBorderStyle = () => {
    // Return border style
    return {border: "2px solid " + props.senator.getColor("primary")};
  }

  const getBgStyle = () => {
    // Get base background color
    let bgColor = props.senator.getColor("bg");

    // Manipulate color to make gradient background
    if (mouseHover === true) {
      bgColor = chroma(bgColor).brighten(1).hex();
    }
    let innerBgColor = chroma(bgColor).brighten().hex();
    let outerBgColor = chroma(bgColor).darken().hex();
    
    // Return background style
    return {background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")"};
  }

  const getPictureClass = () => {
    let cssClass = styles.picture;
    if (!props.senator.alive) {
      cssClass = cssClass + " grayscale-img"
    }
    return cssClass;
  }

  /**
   * Get the correct picture based on the senators name.
   * This will get very long when more senators are included, so this logic should be moved to a helper method.
   */ 
  const getPicture = (): StaticImageData | string => {
    if (props.senator.name === "cornelius") {
      return Cornelius
    } else if (props.senator.name === "fabius") {
      return Fabius
    } else if (props.senator.name === "valerius") {
      return Valerius
    } else if (props.senator.name === "julius") {
      return Julius
    }
    return "";
  }

  // For semantic reasons, use the `a` tag only if the portrait is linked to a senator inspector
  const DynamicTag = props.setInspectorRef ? "a" : "div";

  return (
    <DynamicTag href="#" onMouseEnter={mouseEnter} onMouseLeave={mouseLeave} className={styles.senatorPortrait}>
      <figure ref={portraitRef}>
        <Image className={getPictureClass()} style={getBorderStyle()} src={getPicture()} alt={"Portrait of " + props.senator.getShortName()} />
        <div className={styles.bg} style={getBgStyle()}></div>
        {props.senator.factionLeader && <Image className={styles.factionLeader} src={FactionLeaderPattern} alt="Faction Leader" width="70" />}
        <MajorOfficeIcon majorOffice={props.senator.majorOffice}/>
      </figure>
    </DynamicTag>
  )
}

export default SenatorPortrait;
