import { useEffect, useState } from "react";
import Senator from "../../objects/Senator";
import MajorOfficeIcon from "./MajorOfficeIcon";
import "./SenatorSummary.css";

interface SenatorSummaryProps {
  senator: Senator;
  parentXOffset: number;
  parentYOffset: number;
}

const SenatorSummary = (props: SenatorSummaryProps) => {

  const [height, setHeight] = useState<number>(0);  // 35px is the smallest possible height

  useEffect(() => {
    let newHeight = 70;
    if (props.senator.majorOffice) {
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

    let left = props.parentXOffset + 78;
    if (left + width >= window.innerWidth - minViewportEndOffset) {
      left = props.parentXOffset - width + 2;
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
    if (!props.senator.alive) {
      return <p>Dead</p>
    } else if (props.senator.faction) {
      const factionName = props.senator.getFactionName();

      if (props.senator.factionLeader) {
        return <p>{factionName} Faction <b>Leader</b></p>
      } else {
        return <p>{factionName} Faction</p>
      }
    } else {
      return <p>Unaligned</p>
    }
  }

  const getMajorOffice = () => {
    if (props.senator.majorOffice) {
      return (
        <p>
          {props.senator.majorOffice}
          <MajorOfficeIcon majorOffice={props.senator.majorOffice}/>
        </p>
      )
    }
  }
  
  return (
    <figcaption className='senator-summary' style={getStyle()}>
      <div className="title">
        <h1>{props.senator.name}</h1>
      </div>
      <div className="content">
        {getFaction()}
        {getMajorOffice()}
      </div>
    </figcaption>
  )
}

export default SenatorSummary;
