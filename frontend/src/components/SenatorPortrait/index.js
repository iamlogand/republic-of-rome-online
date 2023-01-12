import { Component } from 'react';
import "./SenatorPortrait.css";
import Cornelius from "../../images/portraits/Cornelius.png";
import RomeConsulIcon from "../../images/icons/RomeConsulIcon.png";

class SenatorPortrait extends Component {
    render() {
        return (
            <div className='senator-portrait'>
                <img className='senator-portrait_picture' src={Cornelius} alt="RomeConsul" width="72" height="72" />
                <img className='senator-portrait_major-office' src={RomeConsulIcon} alt="RomeConsul" width="26" height="26" />
            </div>
        )
    }
}

export default SenatorPortrait;