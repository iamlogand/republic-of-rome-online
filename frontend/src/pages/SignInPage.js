import SignInForm from "../components/SignInForm.js";
import "../css/Auth.css";
import { Component } from 'react';
import { Link } from "react-router-dom";
import TopBar from "../components/TopBar.js"

class SignInPage extends Component {
  render() {
    return (
      <div id="page_container">
        <TopBar username={this.props.username} />
        <div className="auth_area">
          <div>
            <div>
              <div className='auth_box'>
                <div className="auth_title_container">
                  <div className="auth_title">Sign in</div>
                  <div className="auth_link">New here? <Link to="/auth/register" className="underlinedlink">Register a new account</Link></div>
                </div>
                <SignInForm setAuthData={this.props.setAuthData} active={this.props.signInActive} />
              </div>
            </div>
          </div>
          <div className="auth_spacer"></div>
        </div>
      </div>
    );
  }
}

export default SignInPage;
