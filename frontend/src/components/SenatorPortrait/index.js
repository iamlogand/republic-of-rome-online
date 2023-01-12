import { Component } from 'react';
import "./SenatorPortrait.css";
import RomeConsulIcon from "../../images/icons/RomeConsulIcon.png";

class SignInForm extends Component {
    render() {
        return (
            <div className='senator-portrait'>
                <img className='senator-portrait_major-office' src={RomeConsulIcon} alt="RomeConsul" width="30" height="30" />
            </div>
        )
    }
}

export default SignInForm;