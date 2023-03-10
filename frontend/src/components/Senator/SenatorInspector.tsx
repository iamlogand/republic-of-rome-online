import { useEffect, useState } from "react";
import Senator from "../../objects/Senator";
import MajorOfficeIcon from "./MajorOfficeIcon";
import "./SenatorInspector.css";
import SenatorPortrait from "./SenatorPortrait";

interface SenatorInspectorProps {
  instance: Senator;
  XOffset: number;
  YOffset: number;
  width: number;
  showPortrait: boolean;
}

/**
 * The `SenatorInspector` contains a inspector for the senator to which it relates.
 */
const SenatorInspector = (props: SenatorInspectorProps) => {

  const [height, setHeight] = useState<number>(0);

  /**
   * Height of the inspector is determined prior to rendering and is based on the approximate height of it's children
   */
  useEffect(() => {
    let newHeight = 70;
    if (props.showPortrait) {
      newHeight += 84;
    }
    if (props.instance.majorOffice) {
      newHeight += 28;
    }
    setHeight(newHeight);
  }, [props.showPortrait, props.instance.majorOffice]);

  /**
   * Get the style of the root element of SenatorInspector.
   * This function is responsible for setting the size and absolute position of the inspector component.
   * @returns style object with height, width, top and left attributes
   */
  const getStyle = () => {
    const selfWidth = 200;
    const minViewportEndOffset = 10;

    let left = props.XOffset + props.width;
    if (left + selfWidth >= window.innerWidth - minViewportEndOffset) {
      left = props.XOffset - selfWidth;
    }

    let top = props.YOffset;
    if (top + height >= window.innerHeight - minViewportEndOffset) {
      top = window.innerHeight - height - minViewportEndOffset;
    }

    return ({
      height: height,
      width: selfWidth,
      top: top,
      left: left
    })
  }

  const getPortraitStyle = () => {
    // Load background color for use in the background gradient
    const color = props.instance.getColor("bg");
    return ({
      background: `linear-gradient(90deg, var(--bg-color-light), ${color} 40%, ${color} 60%, var(--bg-color-light))`
    })
  }

  /** State the senator's faction. Alternatively, state that they are dead or unaligned */
  const getFaction = () => {
    if (!props.instance.alive) {
      return <p>Dead</p>
    } else if (props.instance.faction) {
      const factionName = props.instance.getFactionName();
      if (props.instance.factionLeader) {
        return <p>{factionName} Faction <b>Leader</b></p>
      } else {
        return <p>{factionName} Faction</p>
      }
    } else {
      return <p>Unaligned</p>
    }
  }
  
  return (
    <dialog open className='senator' style={getStyle()}>
      {props.showPortrait &&
        <div className="portrait" style={getPortraitStyle()}>
          <SenatorPortrait senator={props.instance} setInspectorRef={null} />
        </div>
      }
      <div className="title">
        <h1>{props.instance.name}</h1>
      </div>
      <div className="content">
        {getFaction()}
        {props.instance.majorOffice &&
          <p>
            {props.instance.majorOffice}
            <MajorOfficeIcon majorOffice={props.instance.majorOffice}/>
          </p>
        }
      </div>
    </dialog>
  )
}

export default SenatorInspector;
