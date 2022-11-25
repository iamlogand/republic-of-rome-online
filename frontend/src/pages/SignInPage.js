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
      </div>
    );
  }
}

export default SignInPage;
