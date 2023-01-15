import { Component } from 'react';
import "./SenatorPortrait.css";
import Cornelius from "../../images/portraits/Cornelius-Small.png";
import FactionLeaderPattern from "../../images/patterns/FactionLeader.min.svg";
import RomeConsulIcon from "../../images/icons/RomeConsul.min.svg";
import FieldConsulIcon from "../../images/icons/FieldConsul.min.svg";
import chroma from "chroma-js"

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

  getGetPictureClass = () => {
    let cssClass = "senator-portrait_picture";
    if (this.props.dead) {
      cssClass = cssClass + " grayscale-img"
    }
    return cssClass;
  }

  getFactionLeaderPattern = () => {
    if (this.props.factionLeader === true) {
      return <img className='senator-portrait_faction-leader' src={FactionLeaderPattern} alt="Faction Leader" width="71.5"/>
    }
  }

  getMajorOfficeIcon = () => {
    if (this.props.majorOffice === "Rome Consul") {
      return <img className='senator-portrait_major-office' src={RomeConsulIcon} alt="Rome Consul" width="30" height="30" />
    } else if (this.props.majorOffice === "Field Consul") {
      return <img className='senator-portrait_major-office' src={FieldConsulIcon} alt="Field Consul" width="30" height="30" />
    }
  }

  render() {
    return (
      <div className='senator-portrait' style={this.getStyle()}>
        <img className={this.getGetPictureClass()} src={Cornelius} alt="Cornelius" width="72" height="72" />
        {this.getFactionLeaderPattern()}
        {this.getMajorOfficeIcon()}
      </div>
    )
  }
}

export default SenatorPortrait;