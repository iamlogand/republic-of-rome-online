import { Component } from 'react';
import "../../css/SenatorList.css";
import React from 'react';
import Stat from "./Stat.js"

class Header extends Component {
  render = () => {
    return (
      <div className="senator-list_header">
        <div className="senator-list_header_office"><div>Major Office</div></div>
        <div className="senator-list_header_banner"><div className="senator-list_banner" style={{ backgroundColor: 'white' }}></div></div>
        <div className="senator-list_header_above-portrait"></div>
        <Stat key="military" colName="military" title="Mil"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="oratory" colName="oratory" title="Ora"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="loyalty" colName="loyalty" title="Loy"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="knights" colName="knights" title="Kni"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="influence" colName="influence" title="Inf"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="popularity" colName="popularity" title="Pop"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <Stat key="talents" colName="talents" title="Tal"
          hoverCol={this.props.hoverCol} setHoverCol={this.props.setHoverCol} />
        <div className="senator-list_misc senator-list_header_misc">Miscellaneous</div>
      </div>
    )
  }
}

export default Header;
