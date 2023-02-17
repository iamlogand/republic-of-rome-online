import Senator from "../../objects/Senator";
import "./index.css";

interface SenatorSummaryProps {
  senator: Senator;
  parentXOffset: number;
  parentYOffset: number;
}

const SenatorSummary = (props: SenatorSummaryProps) => {
  const getStyle = () => {
    const width = 200;
    const height = 300;
    const minViewportEndOffset = 10;

    let left = props.parentXOffset + 78;
    if (left + width >= window.innerWidth - minViewportEndOffset) {
      left = props.parentXOffset - 2 - width
    }

    let top = props.parentYOffset;
    if (top + height >= window.innerHeight - minViewportEndOffset) {
      top = window.innerHeight - height - minViewportEndOffset
    }

    return ({
      height: height,
      width: width,
      left: left,
      top: top
    })
  }
  
  return (
    <div className='senator-summary' style={getStyle()}>
      <p>Name: {props.senator.name}</p>
      {props.senator.majorOffice && <p>Major Office: {props.senator.majorOffice}</p>}
      {props.senator.factionLeader && <p>This senator is faction leader</p>}
      {!props.senator.alive && <p>This senator is dead</p>}
    </div>
  )
}

export default SenatorSummary;
