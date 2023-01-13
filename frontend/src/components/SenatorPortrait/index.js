import { Component } from 'react';
import "./SenatorPortrait.css";
import Cornelius from "../../images/portraits/Cornelius-Small.png";
import RomeConsulIcon from "../../images/icons/RomeConsulIcon.png";
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
    let baseColor = this.props.color;
    Object.assign(style, {border: "2px solid " + baseColor});

    // Define background style
    let innerBgColor = chroma.mix(baseColor, 'darkgrey', 0.5).brighten(3).hex();
    let outerBgColor = chroma(baseColor).brighten().hex();
    Object.assign(style, {background: "radial-gradient(" + innerBgColor + ", " + outerBgColor + ")"});
    return style;
  }

  getMajorOffice = () => {
    if (this.props.majorOffice == "consul") {
      return <img className='senator-portrait_major-office' src={RomeConsulIcon} alt="RomeConsul" width="20" height="20" />
    }
  }

  render() {
    return (
      <div className='senator-portrait' style={this.getStyle()}>
        <img className='senator-portrait_picture' src={Cornelius} alt="Cornelius" width="72" height="72" />
        {this.getMajorOffice()}
      </div>
    )
  }
}

export default SenatorPortrait;