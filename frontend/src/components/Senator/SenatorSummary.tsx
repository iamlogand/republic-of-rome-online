import { useEffect, useState } from "react";
import Senator from "../../objects/Senator";
import MajorOfficeIcon from "./MajorOfficeIcon";
import "./SenatorSummary.css";

interface SenatorSummaryProps {
  instance: Senator;
  parentXOffset: number;
  parentYOffset: number;
  parentWidth: number
}

const SenatorSummary = (props: SenatorSummaryProps) => {

  const [height, setHeight] = useState<number>(0);

  useEffect(() => {
    let newHeight = 70;
    if (props.instance.majorOffice) {
      newHeight += 26;
    }
    setHeight(newHeight)
  });

  /**
   * Get the style of the root element of SenatorSummary, which is a `figcaption`.
   * This function is responsible for setting the size and absolute position of the summary component.
   * @returns style object with height, width, top and left attributes
   */
  const getStyle = () => {
    const width = 200;
    const minViewportEndOffset = 10;

    let left = props.parentXOffset + props.parentWidth;
    if (left + width >= window.innerWidth - minViewportEndOffset) {
      left = props.parentXOffset - width;
    }

    let top = props.parentYOffset;
    if (top + height >= window.innerHeight - minViewportEndOffset) {
      top = window.innerHeight - height - minViewportEndOffset;
    }

    return ({
      height: height,
      width: width,
      top: top,
      left: left
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
