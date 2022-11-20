import SignInForm from "../components/SignInForm.js";
import "../css/Authentication.css";
import { Component } from 'react';
import { Link } from "react-router-dom";

class SignInPage extends Component {
  render() {
    return (
      <div className="autharea">
        <div>
          <div>
            <div className='box'>
              <div className="title-space">
                <div className="title">Sign in</div>
                <div className="link">New here? <Link to="/auth/register" className="underlinedlink">Register a new account</Link></div>
              </div>
              <SignInForm setAuthData={this.props.setAuthData} active={this.props.signInActive} />
            </div>
          </div>
        </div>
        <div className="spacer"></div>
      </div>
    )
  }
}

export default SignInPage;
