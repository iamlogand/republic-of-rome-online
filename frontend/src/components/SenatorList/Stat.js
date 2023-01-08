import { Component } from 'react';
import "../../css/SenatorList.css";
import React from 'react';

class Stat extends Component {
  constructor(props) {
    super(props);
    this.state = {
      style: this.getStyle(),
      prefix: this.getPrefix()
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.hoverCol !== prevProps.hoverCol) {
      this.setState({ style: this.getStyle() })
    }
  }

  mouseEnter = () => {
    this.props.setHoverCol(this.props.colName);
  }

  mouseLeave = () => {
    if (this.state.hoverCol !== this.props.colName) {
      this.props.setHoverCol('');
    }
  }

  // Get the dynamic style for the stat component
  getStyle = () => {
    let style = {};

    // If stat is being hovered, set style colors to light on dark
    if (this.props.colName === this.props.hoverCol) {
      Object.assign(style, { color: 'white', backgroundColor: '#696969' });
    }

    // If the stat is a real integer, use red and green to emphasize the number's sign
    if (this.props.type === "realInt") {
      if (this.props.value > 0) {
        Object.hasOwn(style, 'backgroundColor') ? Object.assign(style, { color: '#cce5cc' }) : Object.assign(style, { color: 'green' });
      } else if (this.props.value < 0) {
        Object.hasOwn(style, 'backgroundColor') ? Object.assign(style, { color: '#ffb2b2' }) : Object.assign(style, { color: 'red' });
      }
    }
    return style;
  }

  // Append a sign as a prefix for real integers
  getPrefix = () => {
    if (this.props.type === "realInt") {
      if (this.props.value > 0) {
        return '+';
      } else if (this.props.value < 0) {
        return null;
      }
    } else {
      return null
    }
  }

  render = () => {
    if (typeof this.props.title !== "undefined") {
      return (
        <div className="senator-list_stat noselect"
          onMouseEnter={this.mouseEnter} onMouseLeave={this.mouseLeave}
          style={this.state.style}>{this.props.title}</div>
      );
    }
    if (this.props.value !== 0) {
      return (
        <div className="senator-list_stat noselect"
          onMouseEnter={this.mouseEnter} onMouseLeave={this.mouseLeave}
          style={this.state.style}>{this.state.prefix}{this.props.value}</div>
      );
    } else {
      return (
        <div className="senator-list_stat noselect"
          onMouseEnter={this.mouseEnter} onMouseLeave={this.mouseLeave}
          style={this.state.style}></div>
      );
    }

  }
}

export default Stat;
