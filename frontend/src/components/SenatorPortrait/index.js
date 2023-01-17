import { Component } from 'react';
import "./SenatorPortrait.css";
import chroma from "chroma-js"

import Cornelius from "../../images/portraits/Cornelius.72.png";
import Fabius from "../../images/portraits/Fabius.72.png";

import FactionLeaderPattern from "../../images/patterns/FactionLeader.min.svg";
import RomeConsulIcon from "../../images/icons/RomeConsul.min.svg";
import FieldConsulIcon from "../../images/icons/FieldConsul.min.svg";
import CensorIcon from "../../images/icons/Censor.min.svg";


class SenatorPortrait extends Component {
  constructor(props) {
    super(props);
    this.state = {
      style: this.getStyle()
    };
  }

  getStyle = () => {
    let style = {};

    // Define border style
    const borderColor = this.props.dead ? "black" : this.props.borderColor;
    Object.assign(style, {border: "2px solid " + borderColor});

    // Define background style
    const bgColor = this.props.dead ? "#717171": this.props.bgColor;
    let innerBgColor = chroma(bgColor).brighten().hex();
    let outerBgColor = chroma(bgColor).darken().hex();
    Object.assign(style, {background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")"});
    return style;
  }

  getPictureClass = () => {
    let cssClass = "senator-portrait_picture";
    if (this.props.dead) {
      cssClass = cssClass + " grayscale-img"
    }
    return cssClass;
  }

  getPicture = () => {
    if (this.props.name === "Cornelius") {
      return Cornelius
    } else if (this.props.name === "Fabius") {
      return Fabius
    }
  }

  getFactionLeaderPattern = () => {
    if (this.props.factionLeader === true) {
      return <img className='senator-portrait_faction-leader' src={FactionLeaderPattern} alt="Faction Leader" width="70"/>
    }
  }

  getMajorOfficeIcon = () => {
    if (this.props.majorOffice === "Rome Consul") {
      return <img className='senator-portrait_major-office' src={RomeConsulIcon} alt="Rome Consul" width="30" height="30" />
    } else if (this.props.majorOffice === "Field Consul") {
      return <img className='senator-portrait_major-office' src={FieldConsulIcon} alt="Field Consul" width="30" height="30" />
    } else if (this.props.majorOffice === "Censor") {
      return <img className='senator-portrait_major-office' src={CensorIcon} alt="Censor" width="30" height="30" />
    }
  }

  render() {
    return (
      <div className='senator-portrait' style={this.getStyle()}>
        <img className={this.getPictureClass()} src={this.getPicture()} alt={this.props.name} width="72" height="72" />
        {this.getFactionLeaderPattern()}
        {this.getMajorOfficeIcon()}
      </div>
    )
  }
}

export default SenatorPortrait;