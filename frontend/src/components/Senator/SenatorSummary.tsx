import { useEffect, useState } from "react";
import Senator from "../../objects/Senator";
import MajorOfficeIcon from "./MajorOfficeIcon";
import "./SenatorSummary.css";
import SenatorPortrait from "./SenatorPortrait";

interface SenatorSummaryProps {
  instance: Senator;
  XOffset: number;
  YOffset: number;
  width: number;
  showPortrait: boolean;
}

const SenatorSummary = (props: SenatorSummaryProps) => {

  const [height, setHeight] = useState<number>(0);

  useEffect(() => {
    let newHeight = 70;
    if (props.showPortrait) {
      newHeight += 84;
    }
    if (props.instance.majorOffice) {
      newHeight += 28;
    }
    setHeight(newHeight)
  });

  /**
   * Get the style of the root element of SenatorSummary, which is a `figcaption`.
   * This function is responsible for setting the size and absolute position of the summary component.
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
    const color = props.instance.getColor("bg");
    return ({
      background: `linear-gradient(90deg, var(--bg-color-light), ${color} 40%, ${color} 60%, var(--bg-color-light))`
    })
  }

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

  const getMajorOffice = () => {
    if (props.instance.majorOffice) {
      return (
        <p>
          {props.instance.majorOffice}
          <MajorOfficeIcon majorOffice={props.instance.majorOffice}/>
        </p>
      )
    }
  }
  
  return (
    <div className='senator-summary' style={getStyle()}>
      {props.showPortrait &&
        <div className="portrait" style={getPortraitStyle()}>
          <SenatorPortrait senator={props.instance} setSummaryRef={null} />
        </div>}
      <div className="title">
        <h1>{props.instance.name}</h1>
      </div>
      <div className="content">
        {getFaction()}
        {getMajorOffice()}
      </div>
    </div>
  )
}

export default SenatorSummary;
