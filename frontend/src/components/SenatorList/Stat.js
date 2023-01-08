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

  // If props have been updated, update the `style` state
  componentDidUpdate(prevProps) {
    if (this.props.hoverCol !== prevProps.hoverCol) {
      this.setState({ style: this.getStyle() })
    }
  }

  // Get the dynamic style for the stat component
  getStyle = () => {
    let style = {};

    // If the stat is a real integer, use red and green to emphasize the number's sign
    if (this.props.type === "realInt") {
      if (this.props.value > 0) {
        Object.assign(style, { color: 'green' });
      } else if (this.props.value < 0) {
        Object.assign(style, { color: 'red' });
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
      // Title stat
      return (
        <div className="senator-list_stat no-select" style={this.state.style}>{this.props.title}</div>
      );
    }
    
    if (this.props.value !== 0) {
      // Regular non-zero stat on a senator
      return (
        <div className="senator-list_stat no-select" style={this.state.style}>{this.state.prefix}{this.props.value}</div>
      );
    } else {
      // Zero shows as empty
      return (
        <div className="senator-list_stat no-select" style={this.state.style}></div>
      );
    }
  }
}

export default Stat;
