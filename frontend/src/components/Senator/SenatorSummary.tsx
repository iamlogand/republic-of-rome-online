import Senator from "../../objects/Senator";
import MajorOfficeIcon from "./MajorOfficeIcon";
import "./SenatorSummary.css";

interface SenatorSummaryProps {
  senator: Senator;
  parentXOffset: number;
  parentYOffset: number;
}

const SenatorSummary = (props: SenatorSummaryProps) => {
  const getStyle = () => {
    const width = 200;
    const height = 140;
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
      left: left,
      top: top
    })
  }

  const getFactionSummary = () => {
    if (props.senator.factionLeader) {
      return <p>Yellow Faction <b>Leader</b></p>
    } else {
      return <p>Yellow Faction</p>
    }
  }
  
  return (
    <figcaption className='senator-summary' style={getStyle()}>
      <h1>{props.senator.name}</h1>
      {getFactionSummary()}
      {props.senator.majorOffice && (
        <p>
          {props.senator.majorOffice}
          <MajorOfficeIcon majorOffice={props.senator.majorOffice}/>
        </p>
      )}
      {!props.senator.alive && <p>Dead</p>}
    </figcaption>
  )
}

export default SenatorSummary;
