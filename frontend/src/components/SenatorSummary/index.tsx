import { Component } from 'react';

import "./index.css";

interface Props {
  name: string;
  majorOffice: string;
  factionLeader: boolean;
  borderColor: string;
  bgColor: string;
  dead: boolean;
  parentXOffset: number;
  parentYOffset: number;
}

class SenatorSummary extends Component<Props> {
  getStyle = () => {
    const width = 200;
    const height = 300;
    const minViewportEndOffset = 10;

    let left = this.props.parentXOffset + 78;
    if (left + width >= window.innerWidth - minViewportEndOffset) {
      left = this.props.parentXOffset - 2 - width
    }

    let top = this.props.parentYOffset;
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
  
  render = () => {
    return (
      <div className='senator-summary' style={this.getStyle()}>
        <p>Name: {this.props.name}</p>
        {this.props.majorOffice &&<p>Major Office: {this.props.majorOffice}</p>}
        {this.props.factionLeader && <p>This senator is faction leader</p>}
        {this.props.dead && <p>This senator is dead</p>}
      </div>
    )
  }
}

export default SenatorSummary;
