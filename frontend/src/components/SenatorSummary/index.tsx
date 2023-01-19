import React from 'react';
import { Component } from 'react';

import "./index.css";

interface Props {
  name: string;
}

class SenatorSummary extends Component<Props> {
  myRef: React.RefObject<HTMLDivElement>;

  constructor(props: Props) {
    super(props);
    this.myRef = React.createRef();
  }

  render = () => {
    return (
      <div ref={this.myRef} className='senator-summary'>{this.props.name} + {window.innerHeight}</div>
    )
  }
}

export default SenatorSummary;
