import RegisterForm from "../components/RegisterForm.js";
import "../css/Authentication.css";
import { Component } from 'react';
import { Link } from "react-router-dom";

class RegisterPage extends Component {

  render() {
    return (
      <div className="autharea">
        <div>
          <div>
            <div className='box'>
              <div className="title-space">
                <div className="title">Register</div>
                <div className="link">Already have an account? <Link to="/auth/sign-in" className="underlinedlink">Sign in</Link></div>
              </div>
              <RegisterForm setAuthData={this.props.setAuthData} active={this.props.registerActive} />
            </div>
          </div>
        </div>
        <div className="spacer"></div>
      </div>
    )
  }
}

export default RegisterPage;
